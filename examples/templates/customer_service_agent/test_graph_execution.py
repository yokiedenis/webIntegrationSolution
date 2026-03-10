"""Test the customer service agent graph execution."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from nodes import intake, classify, handle, satisfaction


def test_complete_workflow():
    """Test the complete agent workflow with all nodes."""
    print("=" * 60)
    print("Testing Customer Service Agent Workflow")
    print("=" * 60)

    # Test messages covering different issue types
    test_messages = [
        "I forgot my password!",
        "Why was I charged twice? This is ridiculous!",
        "I'm getting an error code 500 when trying to log in.",
        "I want to return my order and get a refund.",
        "What are your hours of operation?",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{'-' * 60}")
        print(f"Test {i}: {message}")
        print(f"{'-' * 60}")

        # Simulate the graph workflow manually
        context = {"customer_message": message}

        # Node 1: Intake
        context = intake.intake_node(context)
        print("\n[INTAKE]")
        print(f"  Customer ID: {context.get('customer_id')}")
        print(f"  Session ID: {context.get('session_id')}")
        print(f"  Status: {context.get('status')}")

        # Node 2: Classify
        context = classify.classify_node(context)
        print("\n[CLASSIFY]")
        print(f"  Issue Type: {context.get('issue_type')}")
        print(f"  Sentiment: {context.get('sentiment'):.2f}")
        print(f"  Method: {context.get('classification_method')}")

        # Node 3: Handle
        context = handle.handle_node(context)
        print("\n[HANDLE]")
        print(f"  Response: {context.get('agent_response')}")
        print(f"  Resolved: {context.get('resolved')}")
        print(f"  Method: {context.get('response_method')}")

        # Node 4: Satisfaction
        context = satisfaction.track_satisfaction_node(context)
        print("\n[SATISFACTION]")
        print(f"  Satisfaction Score: {context.get('satisfaction_score')}")
        print(f"  Ticket Closed: {context.get('ticket_closed')}")
        print(f"  Final Status: {context.get('status')}")

        # Verify all expected fields are present
        required_fields = [
            "customer_id",
            "session_id",
            "issue_type",
            "sentiment",
            "agent_response",
            "resolved",
            "satisfaction_score",
            "ticket_closed",
            "status",
        ]
        missing = [f for f in required_fields if f not in context]
        if missing:
            print(f"\n⚠️  WARNING: Missing fields: {missing}")
        else:
            print("\n✓ All required fields present")

    print("\n" + "=" * 60)
    print("Workflow Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_complete_workflow()
