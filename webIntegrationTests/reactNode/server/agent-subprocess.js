/**
 * Agent Subprocess Manager
 * Spawns and manages the Python agent server as a child process
 * Handles startup, health checks, and graceful shutdown
 */

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import { waitForPort } from "./utils.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class AgentSubprocessManager {
  constructor(options = {}) {
    this.agentProcess = null;
    this.agentPort = options.agentPort || 5001;
    this.pythonPath = options.pythonPath || "python";
    this.agentScript = options.agentScript;
    this.enabled = options.enabled !== false;
    this.maxStartAttempts = options.maxStartAttempts || 3;
    this.startAttempts = 0;
    this.isShuttingDown = false;
  }

  /**
   * Start the Python agent server as a subprocess
   */
  async start() {
    if (!this.enabled) {
      console.log("⚠️  Agent subprocess is disabled");
      return false;
    }

    if (this.agentProcess) {
      console.log(
        "✓ Agent subprocess already running (PID: %d)",
        this.agentProcess.pid,
      );
      return true;
    }

    this.startAttempts++;
    if (this.startAttempts > this.maxStartAttempts) {
      console.error(
        `✗ Failed to start agent subprocess after ${this.maxStartAttempts} attempts`,
      );
      return false;
    }

    console.log(
      `\n📦 Starting Python agent server (Attempt ${this.startAttempts}/${this.maxStartAttempts})...`,
    );

    try {
      // Determine the agent script path
      const agentScriptPath =
        this.agentScript || path.resolve(__dirname, "../agent_server.py");

      // Spawn Python process
      this.agentProcess = spawn(this.pythonPath, [agentScriptPath], {
        stdio: ["pipe", "pipe", "pipe"],
        detached: false,
      });

      // Handle stdout
      this.agentProcess.stdout.on("data", (data) => {
        const message = data.toString().trim();
        if (message) {
          console.log(`[AGENT] ${message}`);
        }
      });

      // Handle stderr
      this.agentProcess.stderr.on("data", (data) => {
        const message = data.toString().trim();
        if (message) {
          console.error(`[AGENT_ERROR] ${message}`);
        }
      });

      // Handle process exit
      this.agentProcess.on("exit", (code, signal) => {
        console.log(
          `⚠️  Agent process exited with code ${code} (signal: ${signal})`,
        );
        this.agentProcess = null;

        // Auto-restart if not intentional shutdown
        if (!this.isShuttingDown && code !== 0) {
          console.log("🔄 Attempting to restart agent...");
          setTimeout(() => this.start(), 2000);
        }
      });

      // Handle process errors
      this.agentProcess.on("error", (error) => {
        console.error(`✗ Failed to spawn agent process: ${error.message}`);
        this.agentProcess = null;
      });

      // Wait for the agent to be ready
      const ready = await waitForPort(
        "localhost",
        this.agentPort,
        30000,
        500, // Check every 500ms
      );

      if (ready) {
        console.log(
          `✓ Agent subprocess started successfully (PID: ${this.agentProcess.pid})`,
        );
        console.log(`  Running on http://localhost:${this.agentPort}`);
        return true;
      } else {
        console.error(
          `✗ Agent subprocess started but did not become ready on port ${this.agentPort}`,
        );
        this.stop();
        return false;
      }
    } catch (error) {
      console.error(`✗ Error starting agent subprocess: ${error.message}`);
      this.agentProcess = null;
      return false;
    }
  }

  /**
   * Stop the Python agent server subprocess
   */
  stop() {
    if (!this.agentProcess) {
      return;
    }

    console.log(
      `\n🛑 Stopping agent subprocess (PID: ${this.agentProcess.pid})`,
    );
    this.isShuttingDown = true;

    try {
      // Send SIGTERM first (graceful shutdown)
      this.agentProcess.kill("SIGTERM");

      // Set timeout to force kill if needed
      const killTimeout = setTimeout(() => {
        if (this.agentProcess) {
          console.warn("Agent did not stop gracefully, forcing kill...");
          this.agentProcess.kill("SIGKILL");
        }
      }, 5000);

      this.agentProcess.once("exit", () => {
        clearTimeout(killTimeout);
        console.log("✓ Agent subprocess stopped");
      });
    } catch (error) {
      console.error(`Error stopping agent subprocess: ${error.message}`);
      this.agentProcess = null;
    }
  }

  /**
   * Check if agent subprocess is running
   */
  isRunning() {
    return this.agentProcess !== null;
  }

  /**
   * Get agent process information
   */
  getStatus() {
    if (!this.enabled) {
      return {
        enabled: false,
        running: false,
        message: "Agent subprocess is disabled",
      };
    }

    if (!this.agentProcess) {
      return {
        enabled: true,
        running: false,
        message: "Agent subprocess is not running",
      };
    }

    return {
      enabled: true,
      running: true,
      pid: this.agentProcess.pid,
      port: this.agentPort,
      uptime: process.uptime(),
      url: `http://localhost:${this.agentPort}`,
    };
  }
}

export default AgentSubprocessManager;
