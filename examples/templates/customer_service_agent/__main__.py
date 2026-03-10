"""Entry point for Customer Service Agent."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import agent directly (framework integration optional)
from agent import create_customer_service_agent

def main():
    """Run the customer service agent."""
    agent = create_customer_service_agent()
    print(f"✅ Created agent: {agent.name}")
    print(f"📝 Description: {agent.description}")
    print("🚀 Ready to process customer inquiries!")

if __name__ == "__main__":
    main()
