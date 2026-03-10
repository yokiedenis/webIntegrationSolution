# 🚀 Python Agent Integration Guide

This guide shows how to integrate the Python customer service agent with the MERN dashboard.

## System Architecture

```
┌─────────────────────┐
│  React Frontend     │ (Port 3000)
│   (Vite)            │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────┐
│  Express Backend    │ (Port 5000)
│   (Node.js)         │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────────────┐
│  Python Agent Server        │ (Port 5001)
│  - Intake Processing        │
│  - Issue Classification     │
│  - FAQ Resolution           │
│  - Satisfaction Tracking    │
└─────────────────────────────┘
```

## Quick Start (3 Steps)

### Option 1: Automatic (All-in-One)

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode
python start_all.py
```

This starts all three services automatically.

### Option 2: Manual (Individual Terminals)

**Terminal 1 - Python Agent Server:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode
python agent_server.py
```

**Terminal 2 - Express Backend:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode\server
npm run dev
```

**Terminal 3 - Vite Frontend:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode\client
npm run dev
```

Then open: **http://localhost:3000**

## How It Works

### 1. Customer sends message

```
User: "I forgot my password"
     ↓
Frontend sends POST /api/support/chat
```

### 2. Express Backend processes

```
Backend receives message
↓
Calls Python Agent Server at localhost:5001/process
↓
Waits for agent response (fallback to mock if unavailable)
```

### 3. Python Agent processes

```
Agent receives message
↓
Intake Node validates inquiry
↓
Classify Node determines issue type (password_reset, billing, technical, etc.)
↓
Handle Node routes to appropriate handler
↓
Returns structured response
```

### 4. Response sent back to frontend

```
Backend receives agent response
↓
Stores in message history
↓
Returns to frontend
↓
User sees intelligent response
```

## API Endpoints

### Frontend → Backend

**Send Message:**

```bash
POST /api/support/chat
Content-Type: application/json

{
  "customer_id": "CUST-12345",
  "session_id": "session-xyz",
  "message": "I forgot my password"
}

Response:
{
  "response": "I can help you reset your password...",
  "issue_type": "password_reset",
  "resolved": true,
  "ticket_id": "TICKET-...",
  "satisfaction_score": 0.95
}
```

**Get History:**

```bash
GET /api/support/history/CUST-12345

Response:
{
  "customer_id": "CUST-12345",
  "messages": [
    {
      "timestamp": "...",
      "user_message": "...",
      "agent_response": "...",
      "issue_type": "..."
    }
  ],
  "total": 5
}
```

**Rate Satisfaction:**

```bash
POST /api/support/rate
Content-Type: application/json

{
  "ticket_id": "TICKET-...",
  "satisfaction_score": 5,
  "feedback": "Excellent support!"
}
```

### Backend → Python Agent

**Process Message:**

```bash
POST http://localhost:5001/process
Content-Type: application/json

{
  "message": "I forgot my password",
  "customer_id": "CUST-12345",
  "session_id": "session-xyz"
}

Response:
{
  "status": "success",
  "agent_response": "I can help you reset your password...",
  "issue_type": "password_reset",
  "resolved": true
}
```

**Health Check:**

```bash
GET http://localhost:5001/health

Response:
{
  "status": "healthy",
  "agent_ready": true
}
```

## Configuration

### Backend Environment (.env)

```bash
PORT=5000
NODE_ENV=development
PYTHON_AGENT_URL=http://localhost:5001
DATABASE_URL=mongodb://localhost:27017/customer_service
```

### Agent Configuration (agent_server.py)

The agent loads configuration from:

```python
examples/templates/customer_service_agent/config.py
```

Current configuration includes:

- FAQ knowledge base
- Issue classification keywords
- Handler routing logic

## Testing

### 1. Test Direct Agent Call

```bash
# Check agent health
curl http://localhost:5001/health

# Send test message
curl -X POST http://localhost:5001/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "password reset",
    "customer_id": "test-user",
    "session_id": "test-session"
  }'
```

### 2. Test Through Backend

```bash
curl -X POST http://localhost:5000/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-user",
    "session_id": "test-session",
    "message": "password reset"
  }'
```

### 3. Test Through UI

1. Open http://localhost:3000
2. Type a message: "password reset"
3. Watch agent respond intelligently
4. Try other messages: "billing", "technical support", "refund"

## Troubleshooting

### ❌ "ECONNREFUSED" on backend

**Problem:** Backend can't reach Python agent
**Solution:** Make sure agent server is running on port 5001

```bash
python agent_server.py
```

### ❌ Python agent imports fail

**Problem:** Can't import customer_service_agent
**Solution:** Check that paths are correct

```bash
# From webIntegrationTests/reactNode directory
python -c "import sys; sys.path.insert(0, '../../examples'); from templates.customer_service_agent import agent; print('OK')"
```

### ❌ Port already in use

**Problem:** "Address already in use"
**Solution:** Kill process using the port

```powershell
# Find process on port
netstat -ano | findstr :5000

# Kill it (replace PID)
taskkill /PID <PID> /F
```

### ✓ Fallback Mode

If agent is unavailable, the backend automatically uses mock responses:

```javascript
// agents/server.js has built-in fallback
return getFallbackResponse(message);
```

## Production Deployment

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  frontend:
    build: ./client
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build: ./server
    ports:
      - "5000:5000"
    environment:
      - PYTHON_AGENT_URL=http://agent:5001
    depends_on:
      - agent

  agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    ports:
      - "5001:5001"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

Then run:

```bash
docker-compose up
```

## Next Steps

1. ✅ Integrate with real MongoDB database
2. ✅ Connect to production LLM (Claude, GPT, etc.)
3. ✅ Add authentication (JWT tokens)
4. ✅ Implement ticket escalation to humans
5. ✅ Add real-time updates (WebSocket)
6. ✅ Deploy to cloud (AWS, Google Cloud, Azure)

---

**Questions?** Check the main README or CUSTOMER_SERVICE_INTEGRATION.md
