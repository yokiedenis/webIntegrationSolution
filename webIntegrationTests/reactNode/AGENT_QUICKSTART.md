# 🚀 Quick Start - Python Agent Integration

Your customer service system is now ready with full Python agent integration!

## Start Everything in 1 Command

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode
python start_all.py
```

This automatically starts:

- ✅ Python Agent Server (port 5001)
- ✅ Express Backend (port 5000)
- ✅ Vite Frontend (port 3000)

Then open: **http://localhost:3000**

---

## Or Start Manually (3 Terminals)

**Terminal 1 - Agent:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode
python agent_server.py
```

**Terminal 2 - Backend:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode\server
npm run dev
```

**Terminal 3 - Frontend:**

```bash
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode\client
npm run dev
```

---

## Test the Integration

### ✅ Agent Health

```bash
curl http://localhost:5001/health
```

### ✅ Send Test Message

```bash
curl -X POST http://localhost:5001/process \
  -H "Content-Type: application/json" \
  -d '{"message": "password reset", "customer_id": "test", "session_id": "test-session"}'
```

### ✅ Through Backend

```bash
curl -X POST http://localhost:5000/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test", "message": "password reset", "session_id": "test-session"}'
```

### ✅ Through UI

Open http://localhost:3000 and:

1. Type: "password reset"
2. See intelligent agent response
3. Try: "billing", "refund", "technical support"

---

## What's New

### Files Created:

- ✅ `agent_server.py` - HTTP wrapper for Python agent
- ✅ `start_all.py` - All-in-one launcher
- ✅ `AGENT_INTEGRATION.md` - Full integration guide
- ✅ Updated `server/server.js` - Real agent calls

### Architecture:

```
UI (React) → Backend (Express) → Agent Server (Python)
                ↓
            Message Processing
                ↓
            Intelligent Responses
```

---

## Features

### Python Agent Does:

- ✅ **Intake** - Validates customer inquiries
- ✅ **Classification** - Detects issue type (password_reset, billing, technical, etc.)
- ✅ **Handling** - Routes to appropriate solution
- ✅ **Satisfaction** - Tracks customer satisfaction

### Backend Features:

- ✅ Message history storage
- ✅ Ticket management
- ✅ Escalation handling
- ✅ Analytics tracking
- ✅ Automatic fallback if agent unavailable

### Frontend Features:

- ✅ Real-time chat UI
- ✅ Message history
- ✅ Escalation button
- ✅ 5-star satisfaction rating
- ✅ Responsive design

---

## Configuration

The agent uses FAQ knowledge base from:

```
examples/templates/customer_service_agent/config.py
```

Current keywords:

- `password_reset`, `forgot`, `reset` → Password Reset
- `billing`, `invoice`, `charge` → Billing
- `error`, `bug`, `technical` → Technical Support
- `refund`, `return`, `money back` → Refunds

---

## Troubleshooting

| Issue                             | Solution                                                 |
| --------------------------------- | -------------------------------------------------------- |
| ECONNREFUSED on /api/support/chat | Make sure agent_server.py is running on 5001             |
| Python import errors              | Check path is correct from webIntegrationTests/reactNode |
| Port already in use               | `taskkill /PID <pid> /F` on Windows                      |
| Agent not responding              | Check `python agent_server.py` output for errors         |

---

## Next: Production Setup

See `AGENT_INTEGRATION.md` for:

- Docker deployment
- MongoDB persistence
- Real LLM integration
- Authentication setup
- Cloud deployment options

---

**Happy building! 🎉**
