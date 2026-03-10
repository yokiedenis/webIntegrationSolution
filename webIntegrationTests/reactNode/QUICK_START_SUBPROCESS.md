# Quick Start: Node Subprocess Agent Integration

## What Changed?

You no longer need to run the agent in a separate bash terminal. The Node.js backend now **automatically spawns and manages the Python agent** as a child process.

## Before (Manual, 3 Terminals)

```bash
# Terminal 1
cd customer_service_agent
python agent_server.py

# Terminal 2
cd reactNode/server
npm run dev

# Terminal 3
cd reactNode/client
npm start
```

## Now (Automatic, 1 Terminal per Component)

```bash
# Terminal 1: Backend with embedded agent
cd reactNode/server
npm run dev
# Agent starts automatically! No separate python command needed

# Terminal 2: Frontend
cd reactNode/client
npm start
```

## One-Time Setup

1. **No additional dependencies** - Uses Node.js built-in `child_process` module
2. **Agent script location** - Automatically finds `../agent_server.py`
3. **Environment variables** - Already configured in `.env`

## How It Works (30-second explanation)

```
npm run dev
   ↓
Express server starts on :5000
   ↓
AgentSubprocessManager.start() called
   ↓
Spawns Python process: python agent_server.py
   ↓
Waits for agent to be ready on :5001
   ↓
Agent ready? ✓ Yes → Continue
         ✗ No  → Retry up to 3 times
   ↓
Frontend can now make requests
```

## Expected Output

```
🚀 Customer Service Dashboard Backend
   Running on http://localhost:5000
   Environment: development
   Python Agent: http://localhost:5001

📦 Starting Python agent server (Attempt 1/3)...
[AGENT] ✓ Agent initialized successfully
[AGENT] Running on http://localhost:5001
✓ Agent subprocess started successfully (PID: 12345)
  Running on http://localhost:5001

Waiting for requests...
```

## Check Agent Status

While backend is running:

```bash
curl http://localhost:5000/api/agent/status
```

Response:

```json
{
  "enabled": true,
  "running": true,
  "pid": 12345,
  "port": 5001,
  "url": "http://localhost:5001"
}
```

## What Happens on Shutdown?

Press `Ctrl+C` → Both backend and agent shut down cleanly

```
^C
⚠️  SIGINT received, shutting down gracefully...
🛑 Stopping agent subprocess (PID: 12345)
✓ Agent subprocess stopped
✓ Server stopped
```

## Features

✅ **Automatic startup** - No manual commands  
✅ **Automatic shutdown** - Clean exit with Ctrl+C  
✅ **Auto-restart** - If agent crashes, it restarts automatically  
✅ **Status monitoring** - Check `/api/agent/status`  
✅ **Unified logging** - All output in one terminal  
✅ **Production ready** - Works with Docker, PM2, systemd

## Troubleshooting

**Agent won't start?**

```bash
# Check if port 5001 is free
netstat -an | findstr 5001

# Check Python is installed
python --version

# Check agent script exists
ls ../agent_server.py
```

**Agent keeps restarting?**

```bash
# Run agent manually to see actual error
cd ..
python agent_server.py
# Look for error messages
```

**Want to disable auto-start?**

```bash
# In .env:
AGENT_SUBPROCESS_ENABLED=false

# Then run agent manually in separate terminal:
python agent_server.py
```

## Configuration

Edit `server/.env`:

```bash
# Port for backend server
PORT=5000

# Agent configuration
AGENT_PORT=5001                    # Port agent runs on
AGENT_SUBPROCESS_ENABLED=true      # Enable/disable auto-start
PYTHON_PATH=python                 # Python executable
```

## Files Modified

- ✅ `server/server.js` - Added agent manager initialization
- ✅ `server/.env` - Added agent configuration
- ✅ `server/agent-subprocess.js` - **NEW** - Manages Python subprocess
- ✅ `server/utils.js` - **NEW** - Helper functions

## Next: Make a Chat Request

```bash
curl -X POST http://localhost:5000/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-123",
    "message": "I forgot my password",
    "session_id": "session-123"
  }'
```

Response:

```json
{
  "response": "I can help you reset your password...",
  "issue_type": "password_reset",
  "resolved": true,
  "satisfaction_score": 0.8
}
```

## That's It!

You're done. The agent integration is complete and automatic. Just run `npm run dev` and everything starts.

For detailed documentation, see: [NODE_SUBPROCESS_INTEGRATION.md](./NODE_SUBPROCESS_INTEGRATION.md)
