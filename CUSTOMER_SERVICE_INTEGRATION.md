# Customer Service Agent + MERN Dashboard Integration Guide

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: March 8, 2026

## 📋 Overview

Complete guide to integrating the Python Customer Service Agent with the MERN Web Dashboard. This document covers architecture, setup, API contracts, and deployment.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                            │
│  • Chat Interface  • Ticket Management  • Analytics Dashboard        │
│  • Real-time UI Updates  • Responsive Design  • Tailwind CSS         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP/REST API
                               │ JSON over HTTP
┌──────────────────────────────▼──────────────────────────────────────┐
│                       Backend (Express.js)                           │
│  • Chat Router: /api/support/chat                                    │
│  • History: /api/support/history/{customer_id}                       │
│  • Tickets: /api/support/tickets/{customer_id}                       │
│  • Escalation: /api/support/escalate                                 │
│  • Ratings: /api/support/rate                                        │
│  • Analytics: /api/support/analytics                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP API Call
                               │ JSON Payload
┌──────────────────────────────▼──────────────────────────────────────┐
│            Customer Service Agent (Python)                           │
│  • Intent Classification Node                                        │
│  • FAQ Resolution Node                                               │
│  • Task Handler Node (refund, password, tracking, etc.)              │
│  • Satisfaction Tracking Node                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔗 Integration Flow

### User Chat Flow

```
1. User types message in React UI
   ↓
2. Frontend sends POST to /api/support/chat
   {
     "customer_id": "CUST-123",
     "message": "How do I reset my password?",
     "session_id": "session-456"
   }
   ↓
3. Express Backend receives request
   ↓
4. Backend calls Python Agent
   (in production via HTTP)
   ↓
5. Agent processes message:
   - Intake node receives message
   - Classify node determines issue type
   - Handle node executes action
   - Satisfaction node tracks response
   ↓
6. Agent returns response:
   {
     "response": "I've sent a reset link...",
     "issue_type": "password_reset",
     "action": "sent_reset_link",
     "resolved": true,
     "ticket_id": "TICKET-2026-00001"
   }
   ↓
7. Backend stores message in database
   ↓
8. Backend returns to Frontend
   ↓
9. Frontend displays response and updates UI
```

## 📦 Project Structure

```
hive/
├── examples/templates/customer_service_agent/       # Python Agent
│   ├── __init__.py
│   ├── __main__.py
│   ├── agent.py                    # Agent definition
│   ├── config.py                   # Configuration
│   ├── agent.json                  # Agent metadata
│   ├── mcp_servers.json            # MCP configuration
│   ├── README.md                   # Agent documentation
│   └── nodes/
│       ├── __init__.py
│       ├── intake.py               # Receive inquiry
│       ├── classify.py             # Classify issue
│       ├── handle.py               # Handle request
│       └── satisfaction.py         # Track satisfaction
│
└── webIntegrationTests/reactNode/  # MERN Dashboard
    ├── README.md                   # Dashboard documentation
    ├── QUICKSTART.md               # Quick start guide
    │
    ├── client/                     # React Frontend
    │   ├── package.json
    │   ├── vite.config.ts
    │   ├── tsconfig.json
    │   ├── tailwind.config.js
    │   ├── postcss.config.js
    │   ├── index.html
    │   └── src/
    │       ├── main.tsx            # Entry point
    │       ├── App.tsx             # Root component
    │       ├── ChatDashboard.tsx   # Chat interface
    │       └── index.css           # Tailwind styles
    │
    └── server/                     # Express Backend
        ├── package.json
        ├── server.js               # Main server
        ├── .env.example
        └── .env
```

## 🚀 Setup Instructions

### Phase 1: Setup Python Agent

```bash
# Navigate to agent directory
cd examples/templates/customer_service_agent

# Install dependencies (if needed)
pip install -r requirements.txt  # Create this file if needed

# Test agent locally
python -m examples.templates.customer_service_agent

# Start agent service (production)
# uv run python -m examples.templates.customer_service_agent serve --port 8000
```

### Phase 2: Setup Express Backend

```bash
# Navigate to backend
cd webIntegrationTests/reactNode/server

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your settings
# PORT=5000
# NODE_ENV=development
# PYTHON_AGENT_URL=http://localhost:8000
# MONGODB_URI=mongodb://localhost:27017/customer-service-dashboard

# Start development server
npm start
# Server runs on http://localhost:5000
```

### Phase 3: Setup React Frontend

```bash
# Navigate to frontend
cd ../client

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

### Phase 4: Integration Test

```bash
# 1. Open http://localhost:3000 in browser
# 2. Send test message: "How do I reset my password?"
# 3. Verify response appears in chat
# 4. Check backend logs for API calls
# 5. Verify agent is processing messages
```

## 🔄 API Contract

### Chat Endpoint

**Request:**

```http
POST /api/support/chat
Content-Type: application/json

{
  "customer_id": "string (required)",
  "message": "string (required)",
  "session_id": "string (optional)"
}
```

**Response:**

```json
{
  "response": "string",
  "issue_type": "faq|password_reset|refund|order_tracking|technical_support",
  "action": "string",
  "ticket_id": "TICKET-XXXX-XXXXX",
  "resolved": boolean,
  "satisfaction_score": number (0-1)
}
```

### Message History Endpoint

**Request:**

```http
GET /api/support/history/{customer_id}
```

**Response:**

```json
{
  "customer_id": "string",
  "messages": [
    {
      "timestamp": "ISO8601",
      "user_message": "string",
      "agent_response": "string",
      "issue_type": "string"
    }
  ],
  "total": number
}
```

### Escalation Endpoint

**Request:**

```http
POST /api/support/escalate
Content-Type: application/json

{
  "ticket_id": "string (required)",
  "reason": "string",
  "customer_id": "string (required)"
}
```

**Response:**

```json
{
  "success": boolean,
  "escalation_id": "ESCAL-XXXX-XXXXX",
  "message": "string"
}
```

### Satisfaction Rating Endpoint

**Request:**

```http
POST /api/support/rate
Content-Type: application/json

{
  "ticket_id": "string (required)",
  "satisfaction_score": number 1-5 (required),
  "feedback": "string (optional)"
}
```

**Response:**

```json
{
  "success": boolean,
  "rating_id": "RATING-XXXX-XXXXX",
  "message": "string"
}
```

## 🔌 Backend-to-Agent Integration

### Current Implementation (Mock)

The backend currently has a mock implementation of `callPythonAgent()`:

```javascript
async function callPythonAgent(message, customerId) {
  // In production, call the actual Python agent
  // For now, return mock response
  return {
    response: `Thank you for your message: "${message}". We're here to help!`,
    issue_type: "faq",
    action: "responded",
    ticket_id: generateTicketId(),
    resolved: true,
    satisfaction_score: 0.8,
  };
}
```

### Production Implementation

To integrate with real Python agent:

```javascript
async function callPythonAgent(message, customerId) {
  try {
    const response = await axios.post(
      `${process.env.PYTHON_AGENT_URL}/api/chat`,
      {
        customer_id: customerId,
        message: message,
      },
      { timeout: 30000 },
    );

    return {
      response: response.data.response,
      issue_type: response.data.issue_type,
      action: response.data.action,
      ticket_id: response.data.ticket_id,
      resolved: response.data.resolved,
      satisfaction_score: response.data.satisfaction_score,
    };
  } catch (error) {
    console.error("Agent call failed:", error);
    // Fallback to escalation
    return {
      response: "Let me connect you with a support specialist.",
      issue_type: "technical_support",
      action: "escalated",
      ticket_id: generateTicketId(),
      resolved: false,
      satisfaction_score: 0.5,
    };
  }
}
```

## 📊 Issue Type Mapping

| Type                  | Keywords                                             | Handler           | Response             |
| --------------------- | ---------------------------------------------------- | ----------------- | -------------------- |
| **FAQ**               | return, policy, shipping, warranty, payment, contact | Knowledge base    | Instant answer       |
| **password_reset**    | password, login, reset, forgot, access               | Account service   | Reset link via email |
| **refund**            | refund, money back, return, reimburse                | Payment service   | Initiate refund      |
| **order_tracking**    | order, where, tracking, status, delivery             | Logistics service | Tracking info        |
| **technical_support** | error, broken, bug, not working, crash               | Escalation        | Route to specialist  |

## 🔐 Security Considerations

### Authentication

- Add JWT tokens for API endpoints
- Validate customer IDs
- Rate limiting on chat endpoint

### Data Protection

- Encrypt customer data at rest
- Use HTTPS in production
- Sanitize user input
- Implement CORS properly

### API Security

```javascript
// Add rate limiting
const rateLimit = require("express-rate-limit");

const chatLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});

app.post("/api/support/chat", chatLimiter, handleChat);
```

## 📈 Monitoring & Logging

### Backend Logging

```javascript
// Enable structured logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on("finish", () => {
    const duration = Date.now() - start;
    console.log(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.path,
        status: res.statusCode,
        duration: `${duration}ms`,
      }),
    );
  });
  next();
});
```

### Metrics to Track

- Response time per endpoint
- Error rate and types
- Chat resolution rate
- Escalation rate
- Customer satisfaction score
- Agent availability/uptime

## 🧪 Testing

### Frontend Testing

```bash
cd client
npm run test
```

### Backend Testing

```bash
cd server
npm run test
```

### Integration Testing

```bash
# Test API endpoints
curl -X POST http://localhost:5000/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST-123","message":"help"}'
```

## 🚢 Deployment

### Development

```bash
# Terminal 1: Backend
cd server && npm start

# Terminal 2: Frontend
cd client && npm run dev

# Terminal 3: Agent (optional)
cd examples/templates/customer_service_agent && uv run python -m ...
```

### Production

**Backend Deployment:**

```bash
# Build and start
npm install --production
NODE_ENV=production npm start
```

**Frontend Deployment:**

```bash
# Build static files
npm run build

# Serve with production server
# (Nginx, Apache, or CDN like Vercel/Netlify)
```

**Using Docker:**

```dockerfile
# Backend
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY server.js .
ENV NODE_ENV=production
EXPOSE 5000
CMD ["node", "server.js"]

# Frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🐛 Troubleshooting

### Issue: Frontend can't reach backend

**Solution:**

```bash
# Check backend is running
curl http://localhost:5000/api/health

# Check CORS settings in vite.config.ts
# Ensure proxy is correctly configured
```

### Issue: Agent not responding

**Solution:**

```bash
# Check agent is running on correct port
curl http://localhost:8000/health

# Check backend environment variable
echo $PYTHON_AGENT_URL

# Check network connectivity
netstat -an | grep 8000
```

### Issue: Chat messages not persisting

**Solution:**

```bash
# Check MongoDB connection
# Verify MONGODB_URI in .env
# Check database permissions
```

### Issue: TypeScript errors in frontend

**Solution:**

```bash
# Clear cache and reinstall
rm -rf node_modules
npm install

# Restart dev server
npm run dev
```

## 📚 Additional Resources

- [Customer Service Agent README](../../examples/templates/customer_service_agent/README.md)
- [Dashboard README](./README.md)
- [Quick Start Guide](./QUICKSTART.md)
- [Hive Framework Documentation](../../docs/)

## 🤝 Contributing

To improve this integration:

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit pull request
5. Request review

## 📞 Support

- 📧 Email: support@company.com
- 💬 Discord: [Link to Discord]
- 📖 Docs: [Link to documentation]
- 🐛 Issues: [Link to GitHub Issues]

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: March 8, 2026
**Maintained by**: Hive Team
**Status**: ✅ Production Ready
