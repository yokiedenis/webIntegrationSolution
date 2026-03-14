/**
 * Server configuration and setup
 */

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import bodyParser from "body-parser";
import AgentSubprocessManager from "./agent-subprocess.js";
import {
  generateCustomerId,
  generateSessionId,
  generateTicketId,
} from "./utils.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const AGENT_PORT = process.env.AGENT_PORT || 5001;
const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:3000";

// Initialize agent subprocess manager
const agentManager = new AgentSubprocessManager({
  agentPort: AGENT_PORT,
  pythonPath: process.env.PYTHON_PATH || "python",
  agentScript: process.env.AGENT_SCRIPT,
  enabled: process.env.AGENT_SUBPROCESS_ENABLED !== "false", // Enabled by default
});

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: "10mb" }));
app.use(bodyParser.urlencoded({ limit: "10mb", extended: true }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// Agent status endpoint
app.get("/api/agent/status", (req, res) => {
  const status = agentManager.getStatus();
  res.json(status);
});

// Chat API Routes
app.post("/api/support/chat", async (req, res) => {
  try {
    const { customer_id, message, session_id } = req.body;

    if (!message || !customer_id) {
      return res.status(400).json({
        error: "Missing required fields: customer_id, message",
      });
    }

    // Call Python agent
    const agentResponse = await callPythonAgent(
      message,
      customer_id,
      session_id,
    );

    // Store message history
    await storeMessage({
      customer_id,
      session_id,
      user_message: message,
      agent_response: agentResponse.response,
      issue_type: agentResponse.issue_type,
      resolved: agentResponse.resolved,
      timestamp: new Date(),
    });

    res.json({
      response: agentResponse.response,
      issue_type: agentResponse.issue_type,
      action: agentResponse.action,
      ticket_id: agentResponse.ticket_id || generateTicketId(),
      resolved: agentResponse.resolved,
      satisfaction_score: agentResponse.satisfaction_score,
    });
  } catch (error) {
    console.error("Chat API error:", error);
    res.status(500).json({
      error: "Failed to process chat message",
      message: error.message,
    });
  }
});

// Get chat history
app.get("/api/support/history/:customer_id", async (req, res) => {
  try {
    const { customer_id } = req.params;
    const history = await getMessageHistory(customer_id);

    res.json({
      customer_id,
      messages: history,
      total: history.length,
    });
  } catch (error) {
    console.error("History API error:", error);
    res.status(500).json({
      error: "Failed to retrieve chat history",
      message: error.message,
    });
  }
});

// Get active tickets
app.get("/api/support/tickets/:customer_id", async (req, res) => {
  try {
    const { customer_id } = req.params;
    const tickets = await getActiveTickets(customer_id);

    res.json({
      customer_id,
      tickets,
      total: tickets.length,
    });
  } catch (error) {
    console.error("Tickets API error:", error);
    res.status(500).json({
      error: "Failed to retrieve tickets",
      message: error.message,
    });
  }
});

// Escalate ticket to human agent
app.post("/api/support/escalate", async (req, res) => {
  try {
    const { ticket_id, reason, customer_id } = req.body;

    const escalation = await escalateTicket({
      ticket_id,
      reason,
      customer_id,
      timestamp: new Date(),
    });

    res.json({
      success: true,
      escalation_id: escalation.id,
      message: "Ticket escalated to human agent",
    });
  } catch (error) {
    console.error("Escalation error:", error);
    res.status(500).json({
      error: "Failed to escalate ticket",
      message: error.message,
    });
  }
});

// Rate satisfaction
app.post("/api/support/rate", async (req, res) => {
  try {
    const { ticket_id, satisfaction_score, feedback } = req.body;

    if (!ticket_id || satisfaction_score === undefined) {
      return res.status(400).json({
        error: "Missing required fields: ticket_id, satisfaction_score",
      });
    }

    const rating = await rateSatisfaction({
      ticket_id,
      satisfaction_score,
      feedback,
      timestamp: new Date(),
    });

    res.json({
      success: true,
      rating_id: rating.id,
      message: "Thank you for your feedback!",
    });
  } catch (error) {
    console.error("Rating error:", error);
    res.status(500).json({
      error: "Failed to save rating",
      message: error.message,
    });
  }
});

// Analytics endpoint
app.get("/api/support/analytics", async (req, res) => {
  try {
    const analytics = await getAnalytics();

    res.json({
      total_tickets: analytics.total_tickets,
      resolved: analytics.resolved,
      escalated: analytics.escalated,
      average_satisfaction: analytics.average_satisfaction,
      response_time_avg: analytics.response_time_avg,
    });
  } catch (error) {
    console.error("Analytics error:", error);
    res.status(500).json({
      error: "Failed to retrieve analytics",
      message: error.message,
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({
    error: "Internal server error",
    message: err.message,
  });
});

// Start server and agent
const server = app.listen(PORT, async () => {
  console.log(`\n🚀 Customer Service Dashboard Backend`);
  console.log(`   Running on http://localhost:${PORT}`);
  console.log(`   Environment: ${process.env.NODE_ENV || "development"}`);
  console.log(`   Python Agent: http://localhost:${AGENT_PORT}`);
  console.log(`   Frontend URL: ${FRONTEND_URL}\n`);

  // Start agent subprocess
  const agentStarted = await agentManager.start();
  if (!agentStarted) {
    console.warn(
      "⚠️  Warning: Agent subprocess failed to start. Chat will use fallback responses.",
    );
  }
});

// Handle graceful shutdown
process.on("SIGTERM", () => {
  console.log("\n⚠️  SIGTERM received, shutting down gracefully...");
  agentManager.stop();
  server.close(() => {
    console.log("✓ Server stopped");
    process.exit(0);
  });
});

process.on("SIGINT", () => {
  console.log("\n⚠️  SIGINT received, shutting down gracefully...");
  agentManager.stop();
  server.close(() => {
    console.log("✓ Server stopped");
    process.exit(0);
  });
});

process.on("uncaughtException", (error) => {
  console.error("Uncaught exception:", error);
  agentManager.stop();
  process.exit(1);
});

// Helper Functions

async function callPythonAgent(message, customerId, sessionId) {
  const pythonAgentUrl = `http://localhost:${AGENT_PORT}`;

  try {
    const response = await fetch(`${pythonAgentUrl}/process`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        customer_id: customerId,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      console.warn(
        `Python agent returned status ${response.status}, using fallback`,
      );
      return getFallbackResponse(message);
    }

    const data = await response.json();

    if (data.status === "error") {
      console.warn("Python agent error:", data.message);
      return getFallbackResponse(message);
    }

    return {
      response: data.agent_response || "Thank you for contacting us.",
      issue_type: data.issue_type || "general",
      action: data.resolved ? "resolved" : "pending",
      ticket_id: generateTicketId(),
      resolved: data.resolved || false,
      satisfaction_score: 0.8,
    };
  } catch (error) {
    console.warn("Failed to reach Python agent:", error.message);
    console.log("Using fallback mock response...");
    return getFallbackResponse(message);
  }
}

function getFallbackResponse(message) {
  // Fallback mock response if Python agent is unavailable
  return {
    response: `Thank you for your message: "${message}". We're here to help!`,
    issue_type: "faq",
    action: "responded",
    ticket_id: generateTicketId(),
    resolved: true,
    satisfaction_score: 0.8,
  };
}

async function storeMessage(messageData) {
  // Store in database
  console.log("Storing message:", messageData);
  return messageData;
}

async function getMessageHistory(customerId) {
  // Retrieve from database
  return [
    {
      timestamp: new Date(),
      user_message: "How do I reset my password?",
      agent_response:
        "I can help you reset your password. Let me send you a reset link.",
      issue_type: "password_reset",
    },
  ];
}

async function getActiveTickets(customerId) {
  // Retrieve from database
  return [
    {
      ticket_id: "TICKET-2026-00001",
      subject: "Password Reset",
      status: "open",
      created_at: new Date(),
      updated_at: new Date(),
    },
  ];
}

async function escalateTicket(escalationData) {
  console.log("Escalating ticket:", escalationData);
  return {
    id: generateTicketId(),
    ...escalationData,
  };
}

async function rateSatisfaction(ratingData) {
  console.log("Rating satisfaction:", ratingData);
  return {
    id: generateTicketId(),
    ...ratingData,
  };
}

async function getAnalytics() {
  return {
    total_tickets: 150,
    resolved: 130,
    escalated: 20,
    average_satisfaction: 4.2,
    response_time_avg: 1.2,
  };
}

export default app;
export { agentManager };
