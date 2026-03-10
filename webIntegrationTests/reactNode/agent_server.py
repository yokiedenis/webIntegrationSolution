#!/usr/bin/env python3
"""
Customer Service Agent Server
Runs as HTTP service on port 5001
Provides /process endpoint for chat message handling
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os

# Add examples path so we can import the agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples"))

try:
    from templates.customer_service_agent.agent import create_customer_service_agent  # type: ignore
except ImportError:
    # Fallback: try direct import
    try:
        from templates.customer_service_agent.agent import (
            create_customer_service_agent,
        )  # type: ignore
    except ImportError:
        # Last resort: create dummy agent
        def create_customer_service_agent():
            class DummyAgent:
                def invoke(self, message):
                    return {
                        "agent_response": f"Mock response to: {message}",
                        "intent": "general",
                        "resolved": True,
                    }

            return DummyAgent()


# Initialize agent once
try:
    agent = create_customer_service_agent()
    print("[OK] Agent initialized successfully", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to initialize agent: {e}", flush=True)
    agent = None


class AgentRequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for agent processing"""

    def do_POST(self):
        """Handle POST requests to /process"""
        path = urlparse(self.path).path

        if path == "/process":
            try:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))

                # Extract message
                customer_message = data.get("message", "")
                session_id = data.get("session_id", "default")
                customer_id = data.get("customer_id", "unknown")

                if not customer_message:
                    self._send_response(
                        {"error": "No message provided", "status": "error"}, 400
                    )
                    return

                # Process with agent
                if agent:
                    try:
                        # Call agent with the message
                        result = agent.invoke(customer_message)

                        self._send_response(
                            {
                                "status": "success",
                                "agent_response": result.get(
                                    "agent_response", "Unable to process your message."
                                ),
                                "intent": result.get("intent", "general"),
                                "sentiment": result.get("sentiment", 0.0),
                                "urgency": result.get("urgency", "medium"),
                                "resolved": result.get("resolved", False),
                                "tool_used": result.get("tool_used"),
                                "tool_result": result.get("tool_result"),
                                "classification_method": result.get(
                                    "classification_method", "keyword"
                                ),
                                "processing_time_ms": result.get(
                                    "processing_time_ms", 0
                                ),
                                "customer_id": customer_id,
                                "session_id": session_id,
                            },
                            200,
                        )

                    except Exception as agent_error:
                        print(f"Agent processing error: {agent_error}", flush=True)
                        self._send_response(
                            {
                                "status": "error",
                                "message": f"Agent error: {str(agent_error)}",
                                "agent_response": "Thank you for contacting us. Please try again in a moment.",
                            },
                            500,
                        )
                else:
                    # Fallback if agent not initialized
                    self._send_response(
                        {
                            "status": "error",
                            "message": "Agent not initialized",
                            "agent_response": "The service is temporarily unavailable. Please try again later.",
                        },
                        503,
                    )

            except json.JSONDecodeError:
                self._send_response(
                    {"error": "Invalid JSON in request body", "status": "error"}, 400
                )
            except Exception as e:
                print(f"Request processing error: {e}", flush=True)
                self._send_response({"error": str(e), "status": "error"}, 500)

        elif path == "/health":
            self._send_response(
                {"status": "healthy", "agent_ready": agent is not None}, 200
            )

        else:
            self._send_response(
                {"error": "Not Found", "available_endpoints": ["/process", "/health"]},
                404,
            )

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_response(self, data: dict, status_code: int):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        response_body = json.dumps(data).encode("utf-8")
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    """Start the agent HTTP server"""
    port = 5001
    server_address = ("", port)
    httpd = HTTPServer(server_address, AgentRequestHandler)

    print(
        f"""
Customer Service Agent Server
Running on http://localhost:{port}

Available endpoints:
  POST /process  -> Process customer message
  GET  /health   -> Health check

Waiting for requests...
""",
        flush=True,
    )

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Agent server stopped", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
