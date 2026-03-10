#!/usr/bin/env python3
"""Test the enhanced customer service agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from templates.customer_service_agent.agent import create_customer_service_agent


def test_agent():
    """Test agent with various customer service scenarios."""
    agent = create_customer_service_agent()

    test_cases = [
        "I forgot my password!",
        "Why was I charged twice? This is ridiculous!",
        "What's the status of my order ORDER-12345?",
        "I want to return this product and get a refund.",
        "Tell me about your premium subscription plans.",
        "I need help, the application keeps crashing.",
    ]

    print("=" * 70)
    print("Enhanced Customer Service Agent Test")
    print("=" * 70)

    for i, message in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Customer: {message}")
        print("-" * 70)

        result = agent.invoke(message)

        print(f"Intent: {result['intent']}")
        print(f"Sentiment: {result['sentiment']:.2f}")
        print(f"Urgency: {result['urgency']}")
        print(f"Resolved: {result['resolved']}")
        print(f"Tool Used: {result['tool_used']}")
        if result["tool_result"]:
            print(f"Tool Result: {result['tool_result']}")
        print(f"Method: {result['classification_method']}")
        print(f"Time: {result['processing_time_ms']:.2f}ms")
        print(f"\nAgent: {result['agent_response']}")

    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_agent()
