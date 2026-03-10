#!/usr/bin/env python3
"""
Start all services: Frontend, Backend, and Agent Server
This script manages three terminals/processes:
1. Python Agent Server (port 5001)
2. Express Backend (port 5000)
3. Vite Frontend (port 3000)
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Determine the base directory
BASE_DIR = Path(__file__).parent
AGENT_SERVER = BASE_DIR / "agent_server.py"
SERVER_DIR = BASE_DIR / "server"
CLIENT_DIR = BASE_DIR / "client"

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def start_service(name, command, cwd, env_vars=None):
    """Start a service in subprocess"""
    print_header(f"Starting {name}")
    print(f"Command: {' '.join(command)}")
    print(f"Directory: {cwd}\n")

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
        )
        return process
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return None

def main():
    """Start all services"""
    print("\n" + "🚀 " * 20)
    print("\n  CUSTOMER SERVICE SYSTEM - FULL STACK LAUNCHER")
    print("\n" + "🚀 " * 20)

    processes = []

    # 1. Start Python Agent Server
    if AGENT_SERVER.exists():
        print_header("Python Agent Server")
        agent_proc = start_service(
            "Python Agent Server",
            [sys.executable, str(AGENT_SERVER)],
            BASE_DIR,
        )
        if agent_proc:
            processes.append(("Agent Server (5001)", agent_proc))
            time.sleep(2)  # Give agent time to start
    else:
        print(f"✗ Agent server not found at {AGENT_SERVER}")

    # 2. Start Express Backend
    backend_proc = start_service(
        "Express Backend",
        ["npm", "run", "dev"],
        SERVER_DIR,
    )
    if backend_proc:
        processes.append(("Backend (5000)", backend_proc))
        time.sleep(2)

    # 3. Start Vite Frontend
    frontend_proc = start_service(
        "Vite Frontend",
        ["npm", "run", "dev"],
        CLIENT_DIR,
    )
    if frontend_proc:
        processes.append(("Frontend (3000)", frontend_proc))

    # Print summary
    print_header("All Services Started")
    print("""
╔════════════════════════════════════════════════════════╗
║           Customer Service System Running              ║
╚════════════════════════════════════════════════════════╝

📊 Services:
  ✓ Python Agent Server  → http://localhost:5001
  ✓ Express Backend      → http://localhost:5000
  ✓ Vite Frontend        → http://localhost:3000

🌐 Open your browser to: http://localhost:3000

📝 To stop all services: Press Ctrl+C

Available endpoints:
  POST   /api/support/chat        → Send customer message
  GET    /api/support/history/:id → Get chat history
  GET    /api/support/tickets/:id → Get active tickets
  POST   /api/support/escalate    → Escalate issue
  POST   /api/support/rate        → Rate satisfaction
  GET    /api/support/analytics   → Get analytics
  GET    /api/health              → Backend health
  POST   /process                 → Agent process (direct)
  GET    /health                  → Agent health

═══════════════════════════════════════════════════════════
""")

    # Keep processes running
    try:
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all services...\n")
        for name, proc in processes:
            print(f"  Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("\n✓ All services stopped\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
