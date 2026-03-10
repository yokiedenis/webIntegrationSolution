# Deploying Node Subprocess to Render

## Overview

Render is an excellent choice for hosting the Node.js backend with Python agent subprocess. It supports:

- ✅ Node.js applications
- ✅ Background workers (Python scripts)
- ✅ Environment variables
- ✅ Automatic deployments from Git
- ✅ Free tier available
- ✅ Custom domains
- ✅ HTTPS by default

## Architecture on Render

```
┌─────────────────────────────────────────────┐
│         Render Web Service (Node.js)        │
│  Port: Assigned dynamically (e.g., 10000)  │
│                                             │
│  ├─ Express Backend                        │
│  ├─ AgentSubprocessManager                 │
│  └─ Routes:                                 │
│      ├─ GET  /api/health                   │
│      ├─ GET  /api/agent/status             │
│      └─ POST /api/support/chat             │
│                                             │
│      ↓ (spawns child process)              │
│                                             │
│  ├─ Python Agent Server                    │
│  │   (BaseHTTPServer on internal port)     │
│  │                                          │
│  │   ├─ POST /process                      │
│  │   └─ Customer Service Agent             │
│  │       ├─ LLM Classification             │
│  │       ├─ Keyword Fallback               │
│  │       └─ Template Responses             │
│  │                                          │
│  └─ Environment Variables:                 │
│      ├─ GROQ_API_KEY                       │
│      ├─ OPENAI_API_KEY (optional)          │
│      ├─ AGENT_MODEL                        │
│      └─ NODE_ENV=production                │
│                                             │
└─────────────────────────────────────────────┘
         ↑ (HTTPS from client)
    Client Application
```

## Prerequisites

1. **Render Account** - Sign up at https://render.com
2. **Git Repository** - Code pushed to GitHub/GitLab/Gitea
3. **API Keys** - Groq or OpenAI key for LLM

## Step 1: Prepare Repository

### Update package.json

Add start script and engines specification:

**File**: `webIntegrationTests/reactNode/server/package.json`

```json
{
  "name": "customer-service-dashboard-backend",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": "18.x"
  },
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "axios": "^1.6.2",
    "body-parser": "^1.20.2"
  }
}
```

### Add requirements.txt for Python

**File**: `examples/templates/customer_service_agent/requirements.txt`

```
litellm>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```

### Update server.js for Production

Add dynamic PORT binding:

```javascript
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## Step 2: Create Render.yaml Configuration

**File**: `render.yaml`

```yaml
services:
  - type: web
    name: customer-service-backend
    runtime: node
    plan: free # or starter for production
    buildCommand: cd webIntegrationTests/reactNode/server && npm install
    startCommand: cd webIntegrationTests/reactNode/server && npm start

    # Environment variables
    envVars:
      - key: NODE_ENV
        value: production
      - key: AGENT_PORT
        value: 5001
      - key: AGENT_SUBPROCESS_ENABLED
        value: "true"
      - key: PYTHON_PATH
        value: python3
      - key: GROQ_API_KEY
        sync: false # You'll set this in Render dashboard
      - key: OPENAI_API_KEY
        sync: false
      - key: AGENT_MODEL
        value: groq/gemma-7b-it

    # Static site for React frontend (optional)
    staticSite:
      source: webIntegrationTests/reactNode/client/dist
      buildCommand: cd webIntegrationTests/reactNode/client && npm install && npm run build
```

## Step 3: Deploy to Render (Manual)

### Option A: Using Render Dashboard

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub/GitLab account

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the branch (main)

3. **Configure Service**
   - **Name**: `customer-service-backend`
   - **Runtime**: Node
   - **Build Command**: `cd webIntegrationTests/reactNode/server && npm install`
   - **Start Command**: `cd webIntegrationTests/reactNode/server && npm start`

4. **Set Environment Variables**
   - `NODE_ENV`: `production`
   - `AGENT_PORT`: `5001`
   - `AGENT_MODEL`: `groq/gemma-7b-it`
   - `GROQ_API_KEY`: (your API key)
   - `PYTHON_PATH`: `python3`

5. **Deploy**
   - Click "Deploy"
   - Wait 2-5 minutes for build and deployment

### Option B: Using Render.yaml

1. **Push render.yaml to repository**

   ```bash
   git add render.yaml
   git commit -m "Add Render deployment configuration"
   git push
   ```

2. **Create Blueprint**
   - Go to https://dashboard.render.com
   - Click "Blueprints"
   - Connect your repository
   - Click "Create Blueprint from Repository"

3. **Review and Deploy**
   - Render will auto-detect `render.yaml`
   - Set secrets (GROQ_API_KEY, OPENAI_API_KEY)
   - Click "Deploy"

## Step 4: Configure Environment Variables

### In Render Dashboard

1. Go to your service
2. Click "Environment"
3. Add variables:

| Variable                   | Value              | Notes             |
| -------------------------- | ------------------ | ----------------- |
| `NODE_ENV`                 | `production`       | Required          |
| `AGENT_PORT`               | `5001`             | Internal port     |
| `AGENT_SUBPROCESS_ENABLED` | `true`             | Enable agent      |
| `PYTHON_PATH`              | `python3`          | Python executable |
| `AGENT_MODEL`              | `groq/gemma-7b-it` | LLM model         |
| `GROQ_API_KEY`             | `gsk_...`          | Your Groq key     |

**Important**: Use "Secret" type for API keys - they won't be logged.

## Step 5: Configure Python Dependencies

Render automatically installs Node dependencies from `package.json`. For Python, add to build command:

```bash
cd webIntegrationTests/reactNode/server && npm install && python3 -m pip install -r ../../examples/templates/customer_service_agent/requirements.txt
```

Or add to `render.yaml`:

```yaml
buildCommand: |
  cd webIntegrationTests/reactNode/server && npm install
  cd ../../../examples/templates/customer_service_agent
  python3 -m pip install -r requirements.txt
  cd ../../../../webIntegrationTests/reactNode/server
```

## Step 6: Test Deployment

Once deployed, Render will provide a URL (e.g., `https://customer-service-backend-xxxx.onrender.com`)

### Test Health Endpoint

```bash
curl https://customer-service-backend-xxxx.onrender.com/api/health
```

### Test Agent Status

```bash
curl https://customer-service-backend-xxxx.onrender.com/api/agent/status
```

### Test Chat API

```bash
curl -X POST https://customer-service-backend-xxxx.onrender.com/api/support/chat \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-123",
    "message": "hi",
    "session_id": "session-456"
  }'
```

## Advantages of Render

✅ **Easy Setup** - One-click deployment from Git
✅ **Free Tier** - Start for free, upgrade as needed
✅ **Auto-Deploy** - Deploys on git push
✅ **Built-in HTTPS** - Secure by default
✅ **Environment Variables** - Easily manage secrets
✅ **Logs** - Real-time log streaming
✅ **One-Click Redeploy** - Easy to redeploy changes
✅ **Custom Domains** - Use your own domain
✅ **Auto-Scaling** - Scale up as traffic grows

## Limitations & Considerations

⚠️ **Free Tier Limitations**:

- Service spins down after 15 minutes of inactivity
- 0.5 CPU, 512 MB RAM (may be slow for Python)
- No background workers

📊 **For Production**:

- Upgrade to **Starter** plan ($12/month minimum)
- More stable performance
- 24/7 uptime guarantee
- Priority support

## Alternative: Render with Separate Services

For better resource management, deploy as separate services:

1. **Web Service** (Node.js Backend)
   - Runtime: Node
   - Cost: $12/month (Starter)
   - Plan your resource needs

2. **Background Worker** (Python Agent)
   - Runtime: Python
   - Cost: $12/month (Starter)
   - Run agent separately if needed

```
Client → Node Backend (Web Service)
           ↓ (HTTP calls)
         Python Agent (Background Worker)
```

## Cost Comparison

| Tier         | Cost    | Use Case            |
| ------------ | ------- | ------------------- |
| **Free**     | $0      | Development/Testing |
| **Starter**  | $12/mo  | Small production    |
| **Standard** | $42/mo  | Medium production   |
| **Pro**      | $240/mo | Large production    |

## Troubleshooting

### Build Fails

```
Check build log in Render dashboard:
- Services → your-service → Logs
- Look for build errors
- Verify package.json and requirements.txt
```

### Agent Doesn't Start

```
1. Check environment variables are set
2. Verify GROQ_API_KEY or OPENAI_API_KEY
3. Check Python is available (python3 --version)
4. Review runtime logs in dashboard
```

### High Memory Usage

```
- Check if agent subprocess is spawning multiple times
- Verify AGENT_SUBPROCESS_ENABLED=true
- Check for memory leaks in agent code
```

### Slow Responses

```
Free tier limitations:
- Upgrade to Starter plan for better performance
- Consider splitting into multiple services
- Optimize agent code
```

## Files to Update Before Deployment

```
webIntegrationTests/reactNode/server/
├── package.json          ← Update scripts and engines
├── .env                  ← Will be overridden by Render
└── server.js             ← Should use process.env.PORT

examples/templates/customer_service_agent/
├── requirements.txt      ← Create (pip dependencies)
└── .env                  ← Not needed on Render (use Render env vars)

Root:
└── render.yaml           ← Create (deployment config)
```

## Deployment Checklist

- [ ] Code pushed to GitHub/GitLab/Gitea
- [ ] `package.json` has start script
- [ ] `requirements.txt` created with dependencies
- [ ] `render.yaml` configured (or will use dashboard)
- [ ] Render account created
- [ ] Repository connected to Render
- [ ] Environment variables configured
- [ ] Build command verified
- [ ] Start command verified
- [ ] Test endpoints after deployment
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts (optional)

## Next Steps

1. **Sign up** for Render: https://render.com
2. **Connect** your GitHub repository
3. **Create** new Web Service
4. **Configure** environment variables
5. **Deploy** with one click
6. **Test** endpoints
7. **Monitor** logs and performance
8. **Scale** if needed

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Node.js on Render**: https://render.com/docs/deploy-node
- **Environment Variables**: https://render.com/docs/environment-variables
- **Troubleshooting**: https://render.com/docs/troubleshooting

---

**Recommendation**: Start with free tier for development, upgrade to Starter ($12/mo) for reliable production use.
