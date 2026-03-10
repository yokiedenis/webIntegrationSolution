# Customer Service Dashboard - Complete Setup & Deployment Guide

**Version**: 1.0.0
**Last Updated**: March 8, 2026
**Status**: ✅ Ready for Deployment

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [API Documentation](#api-documentation)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

Complete MERN stack customer service solution with:

- **React Frontend**: Real-time chat interface with Tailwind CSS
- **Express Backend**: RESTful API for chat, tickets, escalation, analytics
- **Python Agent**: AI-powered intent classification and task automation
- **Integration**: Seamless communication between all components

### Key Features

✅ Real-time customer support chat
✅ Automatic issue classification
✅ Intelligent task routing
✅ Escalation management
✅ Satisfaction tracking
✅ Message history persistence
✅ Analytics dashboard
✅ Production-ready security

---

## 🔧 Prerequisites

### System Requirements

- Node.js 16+ (for frontend and backend)
- npm or yarn
- Python 3.10+ (for agent, optional for initial setup)
- MongoDB (optional, for persistence)

### Installation Verification

```powershell
# Check Node.js
node --version    # Should be v16+
npm --version     # Should be 8+

# Check Python (optional)
python --version  # Should be 3.10+
```

---

## 🚀 Development Setup

### Step 1: Clone and Navigate

```powershell
# Navigate to project root
cd C:\Users\yokas\Desktop\yokie\hive\hive

# Verify you're on main branch
git branch
# Output should show: * main
```

### Step 2: Install Frontend Dependencies

```powershell
cd webIntegrationTests\reactNode\client

# Install all dependencies
npm install

# Verify installation
npm list react          # Should show react version
npm list tailwindcss    # Should show tailwindcss version
npm list vite           # Should show vite version

# Start development server
npm run dev

# Output should show:
# VITE v5.0.2 running at:
# ➜ Local:   http://localhost:3000/
```

### Step 3: Install Backend Dependencies

```powershell
cd ..\server

# Install all dependencies
npm install

# Verify installation
npm list express        # Should show express version
npm list axios          # Should show axios version

# Create .env file
copy .env.example .env

# Edit .env with your settings (use Notepad or VS Code)
# PORT=5000
# NODE_ENV=development
# PYTHON_AGENT_URL=http://localhost:8000

# Start development server
npm start

# Output should show:
# 🚀 Customer Service Dashboard Backend
#    Running on http://localhost:5000
```

### Step 4: Optional - Setup Python Agent

```powershell
# Navigate to agent directory
cd ..\..\..\..\examples\templates\customer_service_agent

# The agent is ready to use (mock implementation included)
# For production, integrate with real Python agent on port 8000
```

### Step 5: Test the Setup

```powershell
# In browser, open:
# http://localhost:3000

# Try sending a message:
# "How do I reset my password?"

# Expected response:
# "I've sent a password reset link to your email..."
```

---

## 📂 Project Structure

```
webIntegrationTests/reactNode/
│
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── .gitignore                         # Git ignore rules
│
├── client/                            # React Frontend
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript config
│   ├── tsconfig.node.json
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js              # PostCSS config
│   ├── index.html                     # HTML template
│   ├── .gitignore
│   │
│   └── src/
│       ├── main.tsx                   # React entry point
│       ├── App.tsx                    # Root component
│       ├── ChatDashboard.tsx          # Chat interface component
│       ├── index.css                  # Global styles (Tailwind)
│       └── vite-env.d.ts              # Vite environment types
│
├── server/                            # Express Backend
│   ├── package.json
│   ├── package-lock.json
│   ├── server.js                      # Main Express server
│   ├── .env.example                   # Environment template
│   ├── .env                           # Environment variables (local)
│   ├── .gitignore
│   │
│   └── node_modules/                  # Dependencies (installed)
│
└── node_modules/                      # Frontend dependencies (installed)
```

---

## 📡 API Documentation

### Base URL

```
Development:  http://localhost:5000
Production:   https://api.example.com
```

### Endpoints

#### 1. Health Check

```http
GET /api/health

Response 200:
{
  "status": "ok",
  "timestamp": "2026-03-08T10:30:00.000Z",
  "uptime": 3600
}
```

#### 2. Send Chat Message

```http
POST /api/support/chat
Content-Type: application/json

Request:
{
  "customer_id": "CUST-123",
  "message": "How do I reset my password?",
  "session_id": "session-456"
}

Response 200:
{
  "response": "I've sent a password reset link to your email.",
  "issue_type": "password_reset",
  "action": "sent_reset_link",
  "ticket_id": "TICKET-2026-00001",
  "resolved": true,
  "satisfaction_score": 0.8
}
```

#### 3. Get Chat History

```http
GET /api/support/history/{customer_id}

Response 200:
{
  "customer_id": "CUST-123",
  "messages": [
    {
      "timestamp": "2026-03-08T10:30:00Z",
      "user_message": "How do I reset my password?",
      "agent_response": "I've sent a reset link.",
      "issue_type": "password_reset"
    }
  ],
  "total": 1
}
```

#### 4. Get Active Tickets

```http
GET /api/support/tickets/{customer_id}

Response 200:
{
  "customer_id": "CUST-123",
  "tickets": [
    {
      "ticket_id": "TICKET-2026-00001",
      "subject": "Password Reset",
      "status": "open",
      "created_at": "2026-03-08T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### 5. Escalate Ticket

```http
POST /api/support/escalate
Content-Type: application/json

Request:
{
  "ticket_id": "TICKET-2026-00001",
  "reason": "Customer requested escalation",
  "customer_id": "CUST-123"
}

Response 200:
{
  "success": true,
  "escalation_id": "ESCAL-2026-00001",
  "message": "Ticket escalated to human agent"
}
```

#### 6. Rate Satisfaction

```http
POST /api/support/rate
Content-Type: application/json

Request:
{
  "ticket_id": "TICKET-2026-00001",
  "satisfaction_score": 5,
  "feedback": "Great service!"
}

Response 200:
{
  "success": true,
  "rating_id": "RATING-2026-00001",
  "message": "Thank you for your feedback!"
}
```

#### 7. Get Analytics

```http
GET /api/support/analytics

Response 200:
{
  "total_tickets": 150,
  "resolved": 130,
  "escalated": 20,
  "average_satisfaction": 4.2,
  "response_time_avg": 1.2
}
```

---

## 🧪 Testing

### Manual Testing

#### Test 1: Chat Interface

1. Open http://localhost:3000
2. Send message: "What's your return policy?"
3. Verify agent response appears
4. Check sidebar shows ticket info

#### Test 2: Escalation

1. Send message: "This is broken"
2. Click "Escalate to Agent"
3. Verify status changes to "escalated"

#### Test 3: Satisfaction Rating

1. Send message: "How do I reset my password?"
2. Wait for response
3. Click rating buttons (1-5 stars)
4. Verify success message

### API Testing

```powershell
# Test health endpoint
curl -X GET http://localhost:5000/api/health

# Test chat endpoint
curl -X POST http://localhost:5000/api/support/chat `
  -H "Content-Type: application/json" `
  -d '{
    "customer_id": "CUST-TEST-001",
    "message": "Help please"
  }'

# Test analytics
curl -X GET http://localhost:5000/api/support/analytics
```

### Unit Testing (Ready to Add)

```powershell
# Frontend tests
cd client
npm run test

# Backend tests
cd ../server
npm run test
```

---

## 🚢 Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificate ready
- [ ] Backup strategy in place
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Rate limiting enabled

### Environment Setup

Create `.env` file in backend with production values:

```bash
PORT=5000
NODE_ENV=production
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
JWT_SECRET=<generate_random_key>
PYTHON_AGENT_URL=https://agent.production.com
LOG_LEVEL=info
CORS_ORIGIN=https://dashboard.production.com
```

### Frontend Build

```powershell
cd client

# Create production build
npm run build

# Output in dist/ directory
# Ready to deploy to CDN or static host
```

### Backend Deployment

#### Option 1: Traditional Node.js Server

```powershell
# Install production dependencies only
npm install --production

# Start with PM2 (recommended)
npm install -g pm2
pm2 start server.js --name "customer-service-api"
pm2 save
pm2 startup
```

#### Option 2: Docker Container

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy application
COPY server.js .

# Set environment
ENV NODE_ENV=production
ENV PORT=5000

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/api/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start server
CMD ["node", "server.js"]
```

Build and run:

```powershell
# Build image
docker build -t customer-service-api:1.0.0 .

# Run container
docker run -p 5000:5000 `
  -e NODE_ENV=production `
  -e PYTHON_AGENT_URL=https://agent.prod.com `
  customer-service-api:1.0.0
```

### Reverse Proxy Setup (Nginx)

```nginx
upstream backend {
    server localhost:5000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name dashboard.example.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐛 Troubleshooting

### Frontend Issues

#### Issue: `Cannot find module 'lucide-react'`

```powershell
# Solution: Reinstall dependencies
cd client
rm -r node_modules
npm install
npm run dev
```

#### Issue: Tailwind CSS not loading

```powershell
# Verify files exist
ls tailwind.config.js
ls postcss.config.js

# Restart dev server
npm run dev
```

#### Issue: Port 3000 already in use

```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3001
```

### Backend Issues

#### Issue: `PORT 5000 already in use`

```powershell
# Find process
netstat -ano | findstr :5000

# Kill it
taskkill /PID <PID> /F
```

#### Issue: Cannot connect to Python agent

```powershell
# Check PYTHON_AGENT_URL in .env
cat .env | findstr PYTHON_AGENT_URL

# Test connectivity
curl http://localhost:8000/api/health

# Start mock agent if needed
# (Currently using mock implementation)
```

#### Issue: MongoDB connection error

```powershell
# Verify MONGODB_URI in .env
# Option 1: Use local MongoDB
# mongod

# Option 2: Use MongoDB Atlas cloud
# Update MONGODB_URI in .env
# MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
```

### General Issues

#### Issue: TypeScript errors after npm install

```powershell
# Clear TypeScript cache
rm -r node_modules/.cache

# Reinstall
npm install

# Restart dev server
npm run dev
```

#### Issue: CORS errors in browser console

```powershell
# Verify backend is running
curl http://localhost:5000/api/health

# Check frontend proxy configuration in vite.config.ts
# Ensure target matches backend URL
```

---

## 📊 Monitoring & Logs

### Backend Logs

```powershell
# Enable verbose logging
$env:LOG_LEVEL = "debug"
npm start

# View specific logs
# Look for [timestamp] method path
```

### Frontend Logs

```powershell
# Open browser developer console
F12

# Check Network tab for API requests
# Check Console for JavaScript errors
```

### Production Monitoring

```bash
# View PM2 logs
pm2 logs customer-service-api

# View Docker logs
docker logs container_name

# View Nginx logs
tail -f /var/log/nginx/access.log
```

---

## 📞 Support & Resources

- **Documentation**: See [CUSTOMER_SERVICE_INTEGRATION.md](../../CUSTOMER_SERVICE_INTEGRATION.md)
- **Agent Guide**: See [examples/templates/customer_service_agent/README.md](../../examples/templates/customer_service_agent/README.md)
- **Dashboard README**: See [README.md](./README.md)

---

## ✅ Deployment Checklist

After deployment, verify:

- [ ] Frontend loads at custom domain
- [ ] Backend API responds to health check
- [ ] Chat messages are processed
- [ ] Messages persist in database
- [ ] Escalation workflow works
- [ ] Satisfaction ratings save
- [ ] Analytics endpoint returns data
- [ ] Error handling works correctly
- [ ] Logging captures all requests
- [ ] Monitoring alerts configured

---

## 📄 License

MIT License - See LICENSE for details

---

**Last Updated**: March 8, 2026
**Maintained by**: Hive Team
**Version**: 1.0.0
