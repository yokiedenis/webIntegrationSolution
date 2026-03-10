"""Configuration for Customer Service Agent."""

from dataclasses import dataclass


@dataclass
class AgentMetadata:
    """Agent metadata for TUI discovery and registration."""

    name: str = "Customer Service Agent"
    description: str = "Intelligent customer service agent with NLP capabilities"


@dataclass
class CustomerServiceConfig:
    """Configuration for the customer service agent."""

    name: str = "customer_service_agent"
    description: str = "Intelligent customer service agent that handles inquiries, escalations, and satisfaction tracking"
    version: str = "1.0.0"

    # FAQ Knowledge base
    faq_knowledge_base: dict | None = None

    # Task handlers
    enable_password_reset: bool = True
    enable_refund_processing: bool = True
    enable_order_tracking: bool = True
    enable_technical_support: bool = True

    # Escalation settings
    max_resolution_attempts: int = 3
    escalation_threshold: float = 0.5  # Confidence score threshold for escalation

    # Model settings
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000

    def __post_init__(self):
        """Initialize FAQ knowledge base if not provided."""
        if self.faq_knowledge_base is None:
            self.faq_knowledge_base = {
                "return_policy": "We offer 30-day returns for all products in original condition.",
                "shipping": "Standard shipping takes 5-7 business days. Express shipping available.",
                "warranty": "All products come with 1-year manufacturer's warranty.",
                "payment_methods": "We accept credit cards, PayPal, and Apple Pay.",
                "contact": "Contact us at support@company.com or call 1-800-SUPPORT.",
            }


# Default configuration instance
config = CustomerServiceConfig()
