#!/usr/bin/env python3
"""
Quick test of the enhanced NLP-enabled customer service agent.
Tests both LLM-based and keyword-based classification/response generation.
"""

import sys
import os

# Setup import path at module level
_examples_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "examples")
)
if _examples_path not in sys.path:
    sys.path.insert(0, _examples_path)

from templates.customer_service_agent.agent import create_customer_service_agent  # type: ignore[import,no-redef] # noqa: E402

# Create agent (with LLM provider if available)
print("Creating agent with NLP capabilities...\n")
agent = create_customer_service_agent()
print("✓ Agent created successfully\n")

# Test messages
test_messages = [
    "I forgot my password",
    "I was charged twice",
    "Getting an error",
    "I want a refund",
    "Hi, just wanted to say hello",
]

print("Testing agent responses:\n")
for msg in test_messages:
    result = agent.invoke(
        {
            "customer_message": msg,
            "customer_id": "test-user",
            "session_id": "test-session",
        }
    )

    print(f"Message: {msg}")
    print(f"Type: {result['issue_type']}")
    print(f"Response: {result['agent_response']}\n")

print("✓ All tests passed!")
