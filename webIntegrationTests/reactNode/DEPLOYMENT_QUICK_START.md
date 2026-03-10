# Node Subprocess Deployment - Quick Start

## One-Command Deployment

### Windows

```bash
webIntegrationTests\reactNode\deploy.bat
```

### Linux/Mac

```bash
chmod +x webIntegrationTests/reactNode/deploy.sh
./webIntegrationTests/reactNode/deploy.sh
```

## Manual Deployment (3 Steps)

### Step 1: Install Dependencies

```bash
cd webIntegrationTests/reactNode/server
npm install
cd ../../..
```

### Step 2: Configure Agent

```bash
# Edit agent configuration
# webIntegrationTests/reactNode/server/.env
PORT=5000
AGENT_PORT=5001
AGENT_SUBPROCESS_ENABLED=true
PYTHON_PATH=python
NODE_ENV=development

# Edit customer service agent configuration
# examples/templates/customer_service_agent/.env
AGENT_MODEL=groq/gemma-7b-it
GROQ_API_KEY=gsk_your_key
```

### Step 3: Start Server

```bash
cd webIntegrationTests/reactNode/server
npm run dev
```

## Verify Deployment

### Check Backend Health

```bash
curl http://localhost:5000/api/health
# Expected: {"status":"ok","timestamp":"...","uptime":...}
```

### Check Agent Status

```bash
curl http://localhost:5000/api/agent/status
# Expected: {"enabled":true,"running":true,"pid":XXXX,"port":5001,...}
```

### Test Chat API

```bash
curl -X POST http://localhost:5000/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-123",
    "message": "hi",
    "session_id": "session-456"
  }'
```

## System Architecture

```
React Client (3000)
        ↓
   Backend (5000)
        ↓
  Agent Subprocess (5001)
        ↓
  Customer Service Agent
  ├─ LLM (Groq/OpenAI)
  ├─ Keywords (Offline NLP)
  └─ Templates (Always works)
```

## Features

✅ **Automatic Agent Startup** - Agent subprocess starts when server starts
✅ **Health Monitoring** - Checks agent availability every 500ms  
✅ **Auto-Restart** - Restarts agent if it crashes
✅ **Graceful Shutdown** - Stops agent cleanly when server stops
✅ **Fallback Chain** - LLM → Keywords → Templates (always responds)
✅ **Hot Reload** - nodemon restarts on file changes
✅ **Logging** - All events logged with timestamps

## Ports

- **5000** - Node.js Backend (required)
- **5001** - Python Agent Server (spawned by backend)
- **3000** - React Frontend (optional, separate)

## Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID XXXX /F

# Linux/Mac
lsof -i :5000
kill -9 XXXX
```

### Agent Not Starting

```bash
# Test agent directly
cd examples/templates/customer_service_agent
python __main__.py

# Check configuration
cat .env
```

### Backend Won't Start

```bash
# Check npm installation
npm install

# Check Node version (need 18+)
node --version

# Check for dependency issues
npm audit
```

## Documentation

- **Full Guide**: `DEPLOYMENT_GUIDE.md`
- **Architecture**: `NODE_SUBPROCESS_INTEGRATION.md`
- **Quickstart**: `QUICK_START_SUBPROCESS.md`
- **Agent Config**: `examples/templates/customer_service_agent/MODEL_RESOLUTION.md`

## Next Steps

1. Run deployment script (Windows: `.bat`, Linux/Mac: `.sh`)
2. Verify all endpoints are responding
3. Test chat API with sample message
4. Check logs for any issues
5. Configure API keys (Groq or OpenAI)
6. Start React frontend (optional)

## Support

If you encounter issues:

1. Check terminal logs for error messages
2. Verify `.env` configuration files
3. Test agent works standalone
4. Check port availability
5. Review DEPLOYMENT_GUIDE.md for detailed troubleshooting

---

**Status**: ✅ Fully integrated and ready to deploy
**Last Updated**: March 9, 2026
