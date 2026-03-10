# Node Subprocess Deployment Guide

## Overview

The customer service agent is deployed as a Node.js backend with a Python subprocess for the AI agent.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React Client (Port 3000)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ↓ (HTTP Requests)                                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│        Node.js Backend Server (Port 5000)              │
│  ├─ Express Server                                      │
│  ├─ API Routes (/api/support/chat, /api/health)       │
│  └─ Agent Subprocess Manager                           │
│        ↓ (spawn child process)                          │
├─────────────────────────────────────────────────────────┤
│   Python Agent Server (Port 5001)                      │
│  ├─ HTTP Server (BaseHTTPRequestHandler)               │
│  ├─ /process endpoint                                  │
│  └─ Customer Service Agent                            │
│      ├─ LLM Classification (GPT-4o/Groq)              │
│      ├─ Keyword-based Fallback                         │
│      └─ Template Responses                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Deployment Steps

### 1. Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- Required Python packages (installed in customer_service_agent directory)

### 2. Install Node Dependencies

```bash
cd webIntegrationTests/reactNode/server
npm install
```

### 3. Configure Environment

Edit `.env` file in the server directory:

```env
PORT=5000
AGENT_PORT=5001
AGENT_SUBPROCESS_ENABLED=true
PYTHON_PATH=python
NODE_ENV=development
```

### 4. Configure Agent

Edit `examples/templates/customer_service_agent/.env`:

```env
# Use Groq for free inference
AGENT_MODEL=groq/gemma-7b-it
GROQ_API_KEY=gsk_your_key_here

# Or use OpenAI (recommended for stability)
AGENT_MODEL=gpt-4o
OPENAI_API_KEY=sk-your_key_here
```

### 5. Start the Server

#### Development Mode (with auto-reload)

```bash
cd webIntegrationTests/reactNode/server
npm run dev
```

#### Production Mode

```bash
cd webIntegrationTests/reactNode/server
npm start
```

#### Monitor Output

```
🚀 Customer Service Dashboard Backend
   Running on http://localhost:5000
   Environment: development
   Python Agent: http://localhost:5001

📦 Starting Python agent server...
✓ Agent subprocess started successfully (PID: XXXX)
  Running on http://localhost:5001
```

### 6. Start Client (Separate Terminal)

```bash
cd webIntegrationTests/reactNode/client
npm run dev
```

Open browser to `http://localhost:3000`

## Subprocess Management

### Automatic Features

- ✅ **Auto-start**: Agent subprocess starts when server starts
- ✅ **Health checks**: Monitors agent availability every 500ms
- ✅ **Auto-restart**: Restarts agent if it crashes
- ✅ **Graceful shutdown**: Stops agent cleanly when server stops
- ✅ **Timeout handling**: 30-second timeout for agent startup

### Manual Control (Optional)

```javascript
// Stop agent subprocess
agentManager.stop();

// Check agent status
const status = agentManager.getStatus();
console.log(status);
// Output: { enabled: true, running: true, pid: 5200, port: 5001, ... }
```

## API Endpoints

### Agent Health Check

```bash
GET http://localhost:5000/api/agent/status

Response:
{
  "enabled": true,
  "running": true,
  "pid": 5200,
  "port": 5001,
  "uptime": 125.456,
  "url": "http://localhost:5001"
}
```

### Chat API

```bash
POST http://localhost:5000/api/support/chat

Request:
{
  "customer_id": "CUST-123",
  "session_id": "session-456",
  "message": "I forgot my password"
}

Response:
{
  "response": "I can help you reset your password...",
  "intent": "password_reset",
  "resolved": true,
  "sentiment": 0.2,
  "session_id": "session-456"
}
```

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID XXXX /F
```

### Issue: Python Agent Not Starting

```bash
# Check if Python is installed
python --version

# Check agent directly
cd examples/templates/customer_service_agent
python __main__.py

# Check .env configuration
cat .env
```

### Issue: Agent Subprocess Fails

```bash
# Check agent logs in terminal
# Look for [AGENT_ERROR] prefixed lines

# Verify agent works standalone
python -c "from agent import create_customer_service_agent; agent = create_customer_service_agent(); print('✓ Agent OK')"
```

## Performance Tuning

### Reduce Startup Time

In `agent-subprocess.js`:

```javascript
const agentManager = new AgentSubprocessManager({
  maxStartAttempts: 2, // Reduce from 3
  startTimeout: 15000, // Reduce from 30000 (ms)
});
```

### Increase Health Check Frequency

In `waitForPort()` utility:

```javascript
const ready = await waitForPort(
  "localhost",
  this.agentPort,
  15000, // timeout
  250, // check interval (faster checks)
);
```

## Monitoring & Logging

### Server Logs

- All requests logged with timestamp
- Agent startup/shutdown events
- Error messages prefixed with `[AGENT_ERROR]`

### Agent Logs

- LLM initialization
- Classification results
- Fallback chain execution
- Response generation

### View Logs

```bash
# Server logs appear in terminal running npm run dev
# Agent logs also appear in same terminal with [AGENT] prefix
```

## Deployment Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.8+ installed
- [ ] `npm install` completed
- [ ] `.env` files configured
- [ ] API keys set (Groq or OpenAI)
- [ ] Port 5000 available
- [ ] Port 5001 available
- [ ] Agent works standalone (`python __main__.py`)
- [ ] Server starts (`npm run dev`)
- [ ] Client loads (`npm run dev` in client folder)
- [ ] Chat endpoint responds

## Production Deployment

For production, use a process manager:

### Option 1: PM2

```bash
npm install -g pm2
pm2 start server.js --name "customer-service-api"
pm2 save
```

### Option 2: Docker

```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
RUN apt-get update && apt-get install -y python3
EXPOSE 5000
CMD ["npm", "start"]
```

### Option 3: systemd (Linux)

```ini
[Unit]
Description=Customer Service API
After=network.target

[Service]
Type=simple
User=nodejs
WorkingDirectory=/opt/customer-service-api
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

## File Structure

```
webIntegrationTests/reactNode/
├── server/
│   ├── server.js                 # Express server
│   ├── agent-subprocess.js       # Subprocess manager
│   ├── utils.js                  # Helper utilities
│   ├── package.json              # Dependencies
│   ├── .env                       # Configuration
│   └── node_modules/
├── client/
│   ├── src/
│   ├── package.json
│   └── ...
├── agent_server.py               # Python agent HTTP server
└── test_agent.py                 # Test utilities
```

## Next Steps

1. **Start deployment**: `npm run dev` in server directory
2. **Verify health**: `curl http://localhost:5000/api/health`
3. **Check agent**: `curl http://localhost:5000/api/agent/status`
4. **Test chat**: Use React client or curl agent endpoint
5. **Monitor logs**: Watch terminal for [AGENT] and [AGENT_ERROR] messages

## Support

For issues:

1. Check logs in terminal
2. Verify `.env` configuration
3. Test agent standalone: `python __main__.py`
4. Check port availability
5. Review troubleshooting section
