# Node Subprocess Agent Integration Guide

## Overview

The Node.js backend now manages the Python agent server as a **child subprocess** instead of requiring manual bash terminal execution. This provides:

- ✅ **Automatic startup** - Agent starts when backend starts
- ✅ **Graceful shutdown** - Agent stops cleanly when backend stops
- ✅ **Health monitoring** - Automatic restart on failures
- ✅ **Status tracking** - API endpoint to check agent status
- ✅ **Unified logging** - Agent output shows in backend terminal
- ✅ **Production ready** - No manual terminal management needed

## Architecture

```
┌─────────────────────────────────────────┐
│       Frontend (React on :3000)         │
└────────────────────┬────────────────────┘
                     │ HTTP
                     ↓
┌─────────────────────────────────────────┐
│    Node.js Backend Server (:5000)       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  AgentSubprocessManager         │   │
│  │  (manages Python subprocess)    │   │
│  │                                 │   │
│  │  ┌───────────────────────────┐  │   │
│  │  │ Python Agent (:5001)      │  │   │
│  │  │ - Classification          │  │   │
│  │  │ - Sentiment Analysis      │  │   │
│  │  │ - Response Generation     │  │   │
│  │  └───────────────────────────┘  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Express Routes:                        │
│  - POST /api/support/chat               │
│  - GET  /api/agent/status               │
│  - GET  /api/health                     │
└─────────────────────────────────────────┘
```

## How It Works

### 1. **Backend Startup**

When `npm run dev` starts the Node.js server:

```javascript
const agentManager = new AgentSubprocessManager({
  agentPort: 5001,
  pythonPath: "python",
  enabled: true, // Default: true
});

app.listen(PORT, async () => {
  // Start agent subprocess
  const agentStarted = await agentManager.start();
});
```

**What happens:**

1. Backend starts on port 5000
2. AgentSubprocessManager spawns Python process: `python agent_server.py`
3. Waits for agent to be ready on port 5001 (30-second timeout)
4. Once ready, frontend can start making requests

### 2. **Chat Request Flow**

```
Frontend (React)
    ↓ POST /api/support/chat
Backend (Node)
    ↓ callPythonAgent()
Python Agent (:5001)
    ↓ /process endpoint
Agent processes message
    ↓ returns classification
Backend
    ↓ stores in database
Frontend receives response
```

### 3. **Graceful Shutdown**

When you press Ctrl+C:

```javascript
process.on("SIGINT", () => {
  agentManager.stop(); // Gracefully stop Python process
  server.close(); // Stop Express server
});
```

**What happens:**

1. SIGTERM sent to Python process
2. Agent server shuts down cleanly (5-second timeout)
3. Express server closes
4. Process exits

### 4. **Auto-Restart on Failure**

If agent process crashes:

```javascript
this.agentProcess.on("exit", (code, signal) => {
  if (!this.isShuttingDown && code !== 0) {
    // Auto-restart after 2 seconds
    setTimeout(() => this.start(), 2000);
  }
});
```

## Files

### New Files

#### `server/agent-subprocess.js`

- **Purpose**: Manages Python agent as child process
- **Exports**: `AgentSubprocessManager` class
- **Methods**:
  - `start()` - Start agent subprocess
  - `stop()` - Stop agent subprocess
  - `isRunning()` - Check if running
  - `getStatus()` - Get status object

#### `server/utils.js`

- **Purpose**: Shared utility functions
- **Exports**:
  - `waitForPort()` - Wait for server to be ready
  - `generateCustomerId()` - Generate customer IDs
  - `generateSessionId()` - Generate session IDs
  - `generateTicketId()` - Generate ticket IDs
  - `retryWithBackoff()` - Retry logic

### Modified Files

#### `server/server.js`

- **Added**: Import AgentSubprocessManager
- **Added**: Create agentManager instance
- **Modified**: app.listen() to start agent
- **Added**: /api/agent/status endpoint
- **Added**: Signal handlers for graceful shutdown
- **Modified**: callPythonAgent() uses AGENT_PORT env var

#### `server/.env`

- **Added**: `AGENT_PORT=5001`
- **Added**: `AGENT_SUBPROCESS_ENABLED=true`
- **Added**: `PYTHON_PATH=python`
- **Removed**: `PYTHON_AGENT_URL` (now auto-configured)

## Configuration

### Environment Variables

```bash
# Port for backend server
PORT=5000

# Agent subprocess configuration
AGENT_PORT=5001                          # Port agent runs on
AGENT_SUBPROCESS_ENABLED=true            # Enable/disable agent subprocess
PYTHON_PATH=python                       # Python executable path
# AGENT_SCRIPT=/custom/path/to/agent_server.py  # Custom agent script path
```

### Disable Agent Subprocess

If you want to run the agent manually in a separate terminal:

```bash
# In .env
AGENT_SUBPROCESS_ENABLED=false
```

Then start agent separately:

```bash
cd examples/templates/customer_service_agent
python agent_server.py
```

### Custom Agent Script Path

If agent script is in a non-standard location:

```bash
# In .env
AGENT_SCRIPT=/full/path/to/agent_server.py
```

## API Endpoints

### 1. Chat Endpoint

```bash
POST /api/support/chat

Request:
{
  "customer_id": "CUST-abc123",
  "message": "I forgot my password",
  "session_id": "session-123"
}

Response:
{
  "response": "I can help you reset your password...",
  "issue_type": "password_reset",
  "action": "resolved",
  "ticket_id": "TICKET-...",
  "resolved": true,
  "satisfaction_score": 0.8
}
```

### 2. Agent Status Endpoint

```bash
GET /api/agent/status

Response (if running):
{
  "enabled": true,
  "running": true,
  "pid": 12345,
  "port": 5001,
  "uptime": 125.432,
  "url": "http://localhost:5001"
}

Response (if disabled):
{
  "enabled": false,
  "running": false,
  "message": "Agent subprocess is disabled"
}
```

### 3. Health Check

```bash
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "2026-03-08T17:45:00.000Z",
  "uptime": 125.432
}
```

## Usage

### Start Everything Automatically

```bash
cd webIntegrationTests/reactNode

# Terminal 1: Start backend (agent starts automatically)
npm run dev

# Terminal 2: Start frontend (in different directory)
cd client
npm start
```

**Output in Terminal 1:**

```
🚀 Customer Service Dashboard Backend
   Running on http://localhost:5000
   Environment: development
   Python Agent: http://localhost:5001

📦 Starting Python agent server (Attempt 1/3)...
[AGENT] ✓ Agent initialized successfully
[AGENT] ╔════════════════════════════════════════╗
[AGENT] ║   Customer Service Agent Server        ║
[AGENT] ║   Running on http://localhost:5001     ║
[AGENT] ╚════════════════════════════════════════╝
✓ Agent subprocess started successfully (PID: 12345)
  Running on http://localhost:5001
```

### Monitoring Agent Status

Check if agent is running:

```bash
curl http://localhost:5000/api/agent/status
```

### Manual Control (Advanced)

In Node REPL:

```javascript
import { agentManager } from "./server/server.js";

// Check status
agentManager.getStatus();

// Stop agent manually
agentManager.stop();

// Start agent manually
await agentManager.start();
```

## Troubleshooting

### Agent Fails to Start

**Symptom**: "Agent subprocess started but did not become ready on port 5001"

**Solutions**:

1. Check if port 5001 is available
2. Verify agent_server.py is executable
3. Check Python path: `which python` or `python --version`
4. Look at stderr output in terminal for Python errors

### Agent Keeps Restarting

**Symptom**: Agent restarts every few seconds

**Solutions**:

1. Check agent_server.py for errors
2. Enable verbose logging: Add debug prints to agent-subprocess.js
3. Increase timeout: Change `30000` to `60000` in `waitForPort` call

### Can't Find Python

**Symptom**: "Failed to spawn agent process: ENOENT"

**Solutions**:

```bash
# Find Python path
which python3
which python

# In .env, use full path
PYTHON_PATH=/usr/bin/python3
# or
PYTHON_PATH=C:\Python39\python.exe
```

### Agent Process Hangs on Windows

**Symptom**: Backend starts but agent never becomes ready

**Solutions**:

```bash
# Kill stuck Python processes
taskkill /IM python.exe /F

# Then restart backend
npm run dev
```

### Disable Agent Subprocess for Development

```bash
# .env
AGENT_SUBPROCESS_ENABLED=false

# Run agent separately
python agent_server.py
```

## Performance Considerations

### Startup Time

- Backend startup: ~500ms
- Agent startup: ~2-5 seconds
- **Total**: ~5 seconds (one-time)

### Resource Usage

- Node process: ~50MB
- Python process: ~100-150MB
- **Total**: ~150-200MB

### Latency

- Agent classification: 50-100ms (keyword mode)
- Agent with LLM: 200-500ms (depends on LLM provider)
- Full roundtrip: Add network latency

## Production Deployment

### Docker Setup

```dockerfile
FROM node:18-alpine

# Install Python
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy backend
COPY webIntegrationTests/reactNode/server .

# Install Node dependencies
RUN npm ci

# Expose ports
EXPOSE 5000 5001

# Start backend (agent starts automatically)
CMD ["npm", "run", "dev"]
```

### PM2 Setup

```bash
# Install PM2
npm install -g pm2

# Create ecosystem config
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: "customer-service-backend",
      script: "./server/server.js",
      watch: false,
      env: {
        NODE_ENV: "production",
        PORT: 5000,
        AGENT_PORT: 5001,
        AGENT_SUBPROCESS_ENABLED: "true",
      },
    },
  ],
};
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Monitor
pm2 monit
```

### Systemd Setup (Linux)

```ini
[Unit]
Description=Customer Service Backend
After=network.target

[Service]
Type=simple
User=nodejs
WorkingDirectory=/opt/customer-service
ExecStart=/usr/bin/npm run dev
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Benefits Over Manual Terminal Approach

| Feature           | Manual Terminal      | Node Subprocess        |
| ----------------- | -------------------- | ---------------------- |
| Startup           | Manual (3 terminals) | Automatic (1 terminal) |
| Shutdown          | Manual (3 Ctrl+C)    | Automatic (1 Ctrl+C)   |
| Restart           | Manual               | Automatic              |
| Logging           | Separate terminal    | Unified                |
| Production ready  | No                   | Yes                    |
| Docker friendly   | No                   | Yes                    |
| PM2 compatible    | No                   | Yes                    |
| Error handling    | Manual               | Automatic              |
| Status monitoring | Manual               | API endpoint           |

## Next Steps

1. ✅ **Installed**: Agent subprocess manager
2. ✅ **Configured**: Environment variables
3. ✅ **Added**: Status endpoint
4. 🔄 **Run**: `npm run dev` to start everything
5. 📝 **Optional**: Add database integration
6. 🚀 **Deploy**: To production with Docker/PM2

## Questions & Support

For issues with subprocess integration:

1. Check agent status: `GET /api/agent/status`
2. Review logs in terminal output
3. Check `.env` configuration
4. Enable debug logging in `agent-subprocess.js`
