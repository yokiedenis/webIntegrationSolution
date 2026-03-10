# Node Subprocess Integration - Implementation Summary

## ✅ Complete

You now have a **production-ready Node subprocess integration** for managing the Python agent server. No more manual bash terminals needed.

## What Was Added

### 1. **Agent Subprocess Manager** (`agent-subprocess.js`)

- Spawns Python agent as child process
- Monitors process health
- Auto-restarts on failures
- Graceful shutdown handling
- 30-second startup timeout
- 3-attempt retry logic

### 2. **Utility Functions** (`utils.js`)

- `waitForPort()` - Detects when server is ready
- `generateCustomerId()` - Creates CUST-XXXXXXXXXX IDs
- `generateSessionId()` - Creates session IDs
- `generateTicketId()` - Creates ticket IDs
- `retryWithBackoff()` - Exponential backoff retry logic
- `logWithPrefix()` - Consistent logging

### 3. **Backend Integration** (Updated `server.js`)

- Imports AgentSubprocessManager
- Creates agent manager instance
- Starts agent on app startup
- Handles graceful shutdown (SIGTERM, SIGINT)
- Adds `/api/agent/status` endpoint
- Uses `AGENT_PORT` env variable

### 4. **Configuration** (Updated `.env`)

```bash
PORT=5000
AGENT_PORT=5001
AGENT_SUBPROCESS_ENABLED=true
PYTHON_PATH=python
```

## Architecture

```
┌─────────────────────────────────────────┐
│    npm run dev (Node.js Backend)        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ AgentSubprocessManager          │   │
│  │  - spawn()                      │   │
│  │  - start()                      │   │
│  │  - stop()                       │   │
│  │  - getStatus()                  │   │
│  │  - auto-restart                 │   │
│  │                                 │   │
│  │  ↓ Spawns                       │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Python Agent Process    │    │   │
│  │  │ (:5001)                 │    │   │
│  │  │                         │    │   │
│  │  │ - Classification        │    │   │
│  │  │ - Sentiment Analysis    │    │   │
│  │  │ - Response Generation   │    │   │
│  │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Execution Flow

### Startup Sequence

```
1. npm run dev
   ↓
2. Express server initializes
   ↓
3. app.listen(5000) called
   ↓
4. agentManager.start() called
   ↓
5. spawn('python', ['agent_server.py'])
   ↓
6. Listen for stdout/stderr
   ↓
7. waitForPort('localhost', 5001, 30000)
   ↓
8. Port responds? → start() returns true
   Port silent?   → retry (3 times) → fail and log warning
   ↓
9. Backend ready on :5000, Agent ready on :5001
```

### Chat Request Sequence

```
Frontend POST /api/support/chat
   ↓
Backend receives request
   ↓
callPythonAgent(message)
   ↓
fetch('http://localhost:5001/process')
   ↓
Python Agent responds
   ↓
Backend stores in DB
   ↓
Frontend receives response with:
   - agent_response
   - issue_type
   - sentiment
   - resolved
   - satisfaction_score
```

### Shutdown Sequence

```
Ctrl+C pressed
   ↓
process.on('SIGINT')
   ↓
agentManager.stop()
   ↓
Send SIGTERM to Python process
   ↓
5-second timeout
   ↓
Process exits? → Close backend
Process hangs? → Send SIGKILL
   ↓
Backend closed
   ↓
Process exits with code 0
```

## API Endpoints

### 1. Chat (Existing - Now Uses Agent)

```
POST /api/support/chat
Content-Type: application/json

{
  "customer_id": "CUST-123",
  "message": "I forgot my password",
  "session_id": "session-123"
}

Response 200:
{
  "response": "I can help you reset...",
  "issue_type": "password_reset",
  "action": "resolved",
  "ticket_id": "TICKET-...",
  "resolved": true,
  "satisfaction_score": 0.8
}
```

### 2. Agent Status (NEW)

```
GET /api/agent/status

Response 200:
{
  "enabled": true,
  "running": true,
  "pid": 12345,
  "port": 5001,
  "uptime": 125.432,
  "url": "http://localhost:5001"
}
```

### 3. Health Check (Existing)

```
GET /api/health

Response 200:
{
  "status": "ok",
  "timestamp": "2026-03-08T18:00:00.000Z",
  "uptime": 125.432
}
```

## How to Use

### Standard Usage (Everything Automatic)

```bash
cd webIntegrationTests/reactNode/server
npm run dev
```

**Output:**

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

Available endpoints:
  POST /api/support/chat
  GET  /api/agent/status
  GET  /api/health
```

### Manual Agent (Disable Subprocess)

```bash
# In server/.env:
AGENT_SUBPROCESS_ENABLED=false

# Terminal 1:
npm run dev

# Terminal 2:
cd ../../examples/templates/customer_service_agent
python agent_server.py
```

### Check Status

```bash
curl http://localhost:5000/api/agent/status
```

## Error Handling

### Agent Fails to Start

**Scenario**: Port 5001 in use / agent script missing

**Behavior**:

- Tries 3 times with 2-second delays
- Logs all failures
- Backend still starts (falls back to mock responses)
- Status endpoint shows: `"running": false, "message": "Agent subprocess is not running"`

### Agent Crashes

**Scenario**: Agent process exits unexpectedly

**Behavior**:

- Detects process exit
- Auto-restarts after 2 seconds
- Repeats up to 3 times
- Falls back to mock if all retries fail

### Port Timeout

**Scenario**: Agent starts but port never responds

**Behavior**:

- Waits 30 seconds for port to respond
- Checks every 500ms
- Times out and retries startup
- Gives up after 3 attempts

## Configuration Options

### Environment Variables

```bash
# Required
PORT=5000

# Agent Management
AGENT_PORT=5001                          # Where agent listens
AGENT_SUBPROCESS_ENABLED=true            # Auto-start agent? (default: true)
PYTHON_PATH=python                       # Python executable
# AGENT_SCRIPT=/custom/path/agent_server.py  # Custom path (optional)
```

### Disable Agent Subprocess

Edit `.env`:

```bash
AGENT_SUBPROCESS_ENABLED=false
```

Then run agent manually:

```bash
python agent_server.py
```

### Custom Python Path

If default `python` doesn't work:

```bash
# macOS/Linux
PYTHON_PATH=/usr/bin/python3
# or
PYTHON_PATH=python3

# Windows
PYTHON_PATH=C:\Python39\python.exe
```

## Production Deployment

### Docker

```dockerfile
FROM node:18-alpine
RUN apk add --no-cache python3
WORKDIR /app
COPY . .
RUN npm ci
EXPOSE 5000 5001
CMD ["npm", "run", "dev"]
```

### PM2

```bash
npm install -g pm2
pm2 start server.js --name "customer-service"
pm2 save
```

### Systemd (Linux)

```ini
[Service]
ExecStart=/usr/bin/npm run dev
Restart=on-failure
RestartSec=10
```

## Benefits vs Manual Terminal

| Aspect            | Manual      | Subprocess      |
| ----------------- | ----------- | --------------- |
| Terminals needed  | 3           | 1               |
| Startup commands  | 3           | 1               |
| Shutdown commands | 3 Ctrl+C    | 1 Ctrl+C        |
| Auto-restart      | ❌ Manual   | ✅ Automatic    |
| Status check      | ❌ Manual   | ✅ API endpoint |
| Production ready  | ❌ No       | ✅ Yes          |
| Docker friendly   | ❌ Complex  | ✅ Simple       |
| PM2 compatible    | ❌ Tricky   | ✅ Direct       |
| Log aggregation   | ❌ Separate | ✅ Unified      |

## File Structure

```
webIntegrationTests/reactNode/
├── server/
│   ├── server.js                 # Updated: added agent manager
│   ├── .env                      # Updated: agent config
│   ├── agent-subprocess.js       # NEW: subprocess manager
│   ├── utils.js                  # NEW: helper functions
│   └── package.json
├── client/
│   └── ...
├── NODE_SUBPROCESS_INTEGRATION.md    # NEW: full docs
└── QUICK_START_SUBPROCESS.md         # NEW: quick guide
```

## Monitoring & Debugging

### Check Agent Status

```bash
curl http://localhost:5000/api/agent/status | jq
```

### Monitor Logs

Output shows all agent messages:

```
[AGENT] ✓ Agent initialized successfully
[AGENT] POST /process
[AGENT] Processing: "I forgot my password"
```

### Debug Mode

Modify `agent-subprocess.js` to add logging:

```javascript
console.log(`[DEBUG] Checking port ${port}...`);
console.log(`[DEBUG] Process stdio configured`);
console.log(`[DEBUG] Waiting for agent ready...`);
```

### Kill Stuck Process

Windows:

```bash
taskkill /IM python.exe /F
```

Unix:

```bash
kill -9 <PID>
# or
pkill -f agent_server.py
```

## Next Steps

1. ✅ **Run**: `npm run dev` (everything starts automatically)
2. ✅ **Test**: Make chat requests via frontend or curl
3. ✅ **Monitor**: Check `/api/agent/status` endpoint
4. 🚀 **Deploy**: Use Docker or PM2 for production
5. 📚 **Learn**: Read `NODE_SUBPROCESS_INTEGRATION.md` for advanced topics

## Support

- **Quick help**: See `QUICK_START_SUBPROCESS.md`
- **Detailed guide**: See `NODE_SUBPROCESS_INTEGRATION.md`
- **Troubleshooting**: Run `npm run dev` and watch terminal output
- **Status check**: `curl http://localhost:5000/api/agent/status`

---

**Status**: ✅ Implementation Complete
**Tested**: ✅ Yes
**Production Ready**: ✅ Yes
**Zero Manual Terminal Management**: ✅ Yes
