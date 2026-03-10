#!/bin/bash
# Customer Service Agent Deployment Scriptpt for Windows
# Starts both Node.js backend and React frontend

set -eal enabledelayedexpansion

echo "🚀 Customer Service Agent Deployment"
echo "===================================="
echo Customer Service Agent Deployment
# Colors for output======================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m's
NC='\033[0m' # No Color.
node --version >nul 2>&1
# Configuration (
BACKEND_DIR="webIntegrationTests/reactNode/server" Node.js 18+
FRONTEND_DIR="webIntegrationTests/reactNode/client"
AGENT_DIR="examples/templates/customer_service_agent"
echo [OK] Node.js installed
# Verify Node.js and Python
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1ersion >nul 2>&1
fi errorlevel 1 (
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"
    if errorlevel 1 (
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python available${NC}"
echo.
# Install backend dependencies
echo -e "\n${YELLOW}Installing backend dependencies...${NC}"
cd "$BACKEND_DIR"ackend dependencies...
if [ ! -d "node_modules" ]; then\server
    npm installode_modules" (
elseecho Installing npm packages...
    echo -e "${GREEN}✓ node_modules already installed${NC}"
fi  if errorlevel 1 (
cd - > /dev/nullROR] Failed to install dependencies
        exit /b 1
# Verify agent configuration
echo -e "\n${YELLOW}Checking agent configuration...${NC}"
if [ ! -f "$AGENT_DIR/.env" ]; theninstalled
    echo -e "${RED}✗ Agent .env not found at $AGENT_DIR/.env${NC}"
    exit 1.
fiho.
echo -e "${GREEN}✓ Agent .env configured${NC}"
REM Check agent configuration
# Check if ports are availableion...
echo -e "\n${YELLOW}Checking port availability...${NC}"\.env" (
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}✗ Port 5000 already in use${NC}"mer_service_agent\.env
    exit 1b 1
fi
echo -e "${GREEN}✓ Port 5000 available${NC}"
echo.
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Port 5001 already in use (will be replaced by subprocess)${NC}"
fiho ====================================
echo -e "${GREEN}✓ Port 5001 will be used by agent${NC}"
echo ====================================
# Start backend
echo -e "\n${YELLOW}Starting backend server...${NC}"
cd "$BACKEND_DIR"tp://localhost:3000
npm run dev &  http://localhost:5001
BACKEND_PID=$!
cd - > /dev/nullrver in 3 seconds...
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo.
# Wait for backend to be ready
echo -e "\n${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; dos backend server...
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; thener to start
        echo -e "${RED}✗ Backend failed to start${NC}"
        kill $BACKEND_PID
        exit 1Open browser
    fi
    sleep 1="Open frontend in browser? (y/n): "
donei "%OPEN%"=="y" (
    start http://localhost:3000
# Check agent status
echo -e "\n${YELLOW}Checking agent status...${NC}"
sleep 2  # Give agent a moment to start
AGENT_STATUS=$(curl -s http://localhost:5000/api/agent/status 2>/dev/null || echo "{}")
if echo "$AGENT_STATUS" | grep -q '"running":true'; then
    echo -e "${GREEN}✓ Agent subprocess is running${NC}"
else.
    echo -e "${YELLOW}⚠ Agent subprocess may still be starting...${NC}"
fiho Close that window to stop the server.
echo.
# Start frontend (optional)
echo -e "\n${YELLOW}Starting frontend (optional)...${NC}"th
read -p "Start React frontend? (y/n) " -n 1 -r00/api/agent/status
echo   Chat API:      POST http://localhost:5000/api/support/chat
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$FRONTEND_DIR"es:
    npm run dev &webIntegrationTests\reactNode\server\.env
    FRONTEND_PID=$!amples\templates\customer_service_agent\.env
    cd - > /dev/null
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
fiuse
# Display summaryecho -e "\n${GREEN}✓ Deployment successful!${NC}"echo -e "\n${YELLOW}Service URLs:${NC}"echo -e "  Backend API:     ${GREEN}http://localhost:5000${NC}"echo -e "  Frontend:        ${GREEN}http://localhost:3000${NC}"echo -e "  Agent Server:    ${GREEN}http://localhost:5001${NC}"echo -e "\n${YELLOW}Endpoints:${NC}"echo -e "  Health Check:    ${GREEN}GET http://localhost:5000/api/health${NC}"echo -e "  Agent Status:    ${GREEN}GET http://localhost:5000/api/agent/status${NC}"echo -e "  Chat API:        ${GREEN}POST http://localhost:5000/api/support/chat${NC}"echo -e "\n${YELLOW}Control:${NC}"echo -e "  View logs:       Logs appear in this terminal"echo -e "  Stop backend:    Press Ctrl+C"echo -e "  Configuration:   Edit ${GREEN}$BACKEND_DIR/.env${NC}"echo -e "  Agent config:    Edit ${GREEN}$AGENT_DIR/.env${NC}"# Keep script runningwait
cd c:\Users\yokas\Desktop\yokie\hive\hive\webIntegrationTests\reactNode
deploy.bat
