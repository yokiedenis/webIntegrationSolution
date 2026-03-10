"""Enhanced Customer Service Agent with LLM and Tools."""

import json
import logging
import os
import time
import re
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Import fallback providers
try:
    from llm_fallback_provider import LLMFallbackProvider
    from keyword_provider import KeywordLLMProvider
except ImportError:
    # Fallback if imports fail
    LLMFallbackProvider = None
    KeywordLLMProvider = None


class CustomerServiceTools:
    """Tools available to the customer service agent."""

    @staticmethod
    def check_order_status(order_id: str) -> Dict[str, Any]:
        """Check the status of a customer order."""
        # Mock implementation - replace with real database
        return {
            "order_id": order_id,
            "status": "shipped",
            "tracking_number": f"TRK{order_id[-6:]}",
            "estimated_delivery": "2026-03-12",
            "last_updated": datetime.now().isoformat(),
        }

    @staticmethod
    def initiate_refund(order_id: str, reason: str) -> Dict[str, Any]:
        """Process a refund request."""
        return {
            "success": True,
            "order_id": order_id,
            "refund_id": f"REF{datetime.now().timestamp():.0f}",
            "status": "initiated",
            "estimated_completion": "2026-03-15",
            "amount": 99.99,  # Mock amount
        }

    @staticmethod
    def reset_password(email: str) -> Dict[str, Any]:
        """Send password reset link."""
        return {
            "success": True,
            "email": email,
            "reset_link_sent": True,
            "expires_in": "24 hours",
        }

    @staticmethod
    def create_support_ticket(subject: str, description: str) -> Dict[str, Any]:
        """Create a support ticket for escalation."""
        return {
            "ticket_id": f"TICKET-{datetime.now().timestamp():.0f}",
            "subject": subject,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "assigned_to": "support_team",
        }

    @staticmethod
    def get_product_info(product_id: str) -> Dict[str, Any]:
        """Get product information."""
        products = {
            "PROD-001": {
                "name": "Premium Subscription",
                "price": "$99/month",
                "features": ["24/7 support", "Priority handling", "Custom features"],
            },
            "PROD-002": {
                "name": "Standard Subscription",
                "price": "$49/month",
                "features": ["Email support", "Standard handling"],
            },
        }
        return products.get(product_id, {"error": "Product not found"})

    @staticmethod
    def check_account_balance(account_id: str) -> Dict[str, Any]:
        """Check customer account balance."""
        return {
            "account_id": account_id,
            "balance": 250.50,
            "currency": "USD",
            "status": "active",
        }


class LLMClient:
    """Lightweight LLM client using litellm."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("AGENT_MODEL", "groq/llama-3.1-70b-versatile")
        self.available = False
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client."""
        try:
            import litellm

            if self.api_key:
                litellm.api_key = self.api_key
                self.client = litellm
                self.available = True
                logger.info(f"LLM client initialized: {self.model}")
            else:
                logger.warning(
                    "No API key configured, using keyword-based classification"
                )
        except ImportError:
            logger.warning("litellm not installed, using keyword-based fallback")

    def classify_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Classify customer intent using LLM."""
        if not self.available:
            return None

        try:
            response = self.client.completion(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Classify this customer message and extract intent, sentiment, and urgency.

Message: "{message}"

Respond in JSON format:
{{
  "intent": "password_reset|billing|technical|refund|product_info|escalation|general",
  "sentiment": -1.0 to 1.0,
  "urgency": "low|medium|high",
  "requires_tool": true|false,
  "tool_name": "check_order|refund|reset_password|create_ticket|product_info|check_balance|none"
}}

Only respond with valid JSON.""",
                    }
                ],
                max_tokens=150,
                temperature=0.3,
            )

            # Extract content from response (litellm returns various formats)
            content: Optional[str] = None
            try:
                # Try standard format
                content = getattr(response.choices[0], "message", None)  # type: ignore
                if content:
                    content = getattr(content, "content", content)
                # Try alternative format
                if not content:
                    content = getattr(response.choices[0], "text", None)  # type: ignore
            except (AttributeError, IndexError, TypeError):
                pass  # Content remains None

            if content:
                result = json.loads(content)
                logger.info(f"LLM classification: {result['intent']}")
                return result
            return None
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            return None

    def generate_response(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate contextual response using LLM."""
        if not self.available:
            return None

        try:
            system_msg = """You are a professional, empathetic customer service agent.
- Be concise and helpful
- Acknowledge customer emotions
- Provide clear next steps
- Use the provided context to personalize responses"""

            response = self.client.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {
                        "role": "user",
                        "content": f"""Customer message: "{message}"

Intent: {context.get("intent", "general")}
Sentiment: {context.get("sentiment", 0.0)}
Urgency: {context.get("urgency", "medium")}

Generate a helpful, empathetic response (2-3 sentences max).""",
                    },
                ],
                max_tokens=200,
                temperature=0.7,
            )

            # Extract content from response (litellm returns various formats)
            content: Optional[str] = None
            try:
                # Try standard format
                content = getattr(response.choices[0], "message", None)  # type: ignore
                if content:
                    content = getattr(content, "content", content)
                # Try alternative format
                if not content:
                    content = getattr(response.choices[0], "text", None)  # type: ignore
            except (AttributeError, IndexError, TypeError):
                pass  # Content remains None

            if content:
                return content.strip()
            return None
        except Exception as e:
            logger.warning(f"LLM response generation failed: {e}")
            return None


class EnhancedAgent:
    """Enhanced Customer Service Agent with tools and LLM."""

    def __init__(self):
        self.name = "customer_service_agent"
        self.description = "Intelligent customer service agent with NLP capabilities"
        self.tools = CustomerServiceTools()
        self.start_time = time.time()

        # Initialize with fallback chain
        self.keyword_provider = KeywordLLMProvider() if KeywordLLMProvider else None
        self.fallback_provider = None

        # Try to initialize fallback provider with LLM
        if LLMFallbackProvider:
            try:
                llm_client = LLMClient()
                self.fallback_provider = LLMFallbackProvider(
                    primary_provider=llm_client
                )
                logger.info("LLMFallbackProvider initialized with primary LLM")
            except Exception as e:
                logger.warning(f"Failed to initialize LLMFallbackProvider: {e}")
                self.fallback_provider = None

        # Fallback to simple LLM client if fallback provider not available
        if not self.fallback_provider:
            self.llm = LLMClient()
        else:
            self.llm = None

        # Keyword fallback for _keyword_classification
        self.keywords = {
            "password_reset": [
                "password",
                "forgot",
                "reset",
                "locked",
                "login",
                "access",
            ],
            "billing": [
                "charge",
                "invoice",
                "payment",
                "bill",
                "refund",
                "cancel",
                "subscription",
            ],
            "technical": [
                "error",
                "bug",
                "crash",
                "not working",
                "broken",
                "issue",
                "problem",
            ],
            "refund": ["refund", "return", "money back", "reimbursement"],
            "product_info": ["price", "feature", "plan", "product", "subscription"],
            "order": ["order", "tracking", "delivery", "shipped", "status"],
        }

    def invoke(self, message: str) -> Dict[str, Any]:
        """Process customer message and return response."""
        start_time = datetime.now()

        # Step 1: Classify intent
        context = self._classify_intent(message)

        # Step 2: Execute tool if needed
        tool_result = None
        if context.get("requires_tool") and context.get("tool_name") != "none":
            tool_result = self._execute_tool(message, context)
            context["tool_result"] = tool_result

        # Step 3: Generate response
        response_text = self._generate_response(message, context)

        # Step 4: Determine resolution status
        resolved = context.get("intent") in [
            "password_reset",
            "billing",
            "product_info",
            "order",
        ]

        return {
            "agent_response": response_text,
            "intent": context.get("intent", "general"),
            "sentiment": context.get("sentiment", 0.0),
            "urgency": context.get("urgency", "medium"),
            "resolved": resolved,
            "tool_used": context.get("tool_name") if tool_result else None,
            "tool_result": tool_result,
            "classification_method": "llm"
            if (self.llm and self.llm.available)
            else "keyword",
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
        }

    def _classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify intent using fallback chain: LLM → Keyword."""
        context = {}

        # Try primary LLM if available
        if self.llm and self.llm.available:
            result = self.llm.classify_intent(message)
            if result:
                context.update(result)
                context["classification_method"] = "llm"
                return context

        # Try fallback provider
        if self.fallback_provider:
            result = self.fallback_provider.classify_intent(message)
            if result:
                context.update(result)
                return context

        # Fallback to keyword provider
        if self.keyword_provider:
            result = self.keyword_provider.classify_intent(message)
            context.update(result)
            return context

        # Last resort: basic keyword classification
        intent = self._keyword_classification(message)
        sentiment = self._analyze_sentiment(message)

        return {
            "intent": intent,
            "sentiment": sentiment,
            "urgency": "high"
            if sentiment < -0.3
            else "medium"
            if sentiment > 0.3
            else "low",
            "requires_tool": intent
            in ["password_reset", "refund", "order", "product_info"],
            "tool_name": self._map_intent_to_tool(intent),
            "classification_method": "keyword",
        }

    def _keyword_classification(self, message: str) -> str:
        """Classify using keywords."""
        msg_lower = message.lower()
        for intent, keywords in self.keywords.items():
            if any(kw in msg_lower for kw in keywords):
                return intent
        return "general"

    def _analyze_sentiment(self, message: str) -> float:
        """Simple sentiment analysis."""
        negative_words = [
            "angry",
            "frustrated",
            "terrible",
            "awful",
            "bad",
            "hate",
            "useless",
            "ridiculous",
        ]
        positive_words = [
            "thanks",
            "appreciate",
            "great",
            "excellent",
            "love",
            "happy",
            "pleased",
        ]

        msg_lower = message.lower()

        negative_score = sum(1 for word in negative_words if word in msg_lower)
        positive_score = sum(1 for word in positive_words if word in msg_lower)

        if negative_score + positive_score == 0:
            return 0.0
        return (positive_score - negative_score) / (positive_score + negative_score)

    def _map_intent_to_tool(self, intent: str) -> str:
        """Map intent to tool name."""
        mapping = {
            "password_reset": "reset_password",
            "refund": "initiate_refund",
            "order": "check_order_status",
            "product_info": "get_product_info",
            "billing": "check_account_balance",
            "escalation": "create_support_ticket",
        }
        return mapping.get(intent, "none")

    def _execute_tool(
        self, message: str, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute appropriate tool based on context."""
        tool_name = context.get("tool_name")

        try:
            if tool_name == "reset_password":
                # Extract email from message or use default
                email = "customer@example.com"  # Could parse from message
                return self.tools.reset_password(email)

            elif tool_name == "initiate_refund":
                # Extract order ID
                order_id = self._extract_order_id(message) or "ORDER-123"
                return self.tools.initiate_refund(order_id, message)

            elif tool_name == "check_order_status":
                order_id = self._extract_order_id(message) or "ORDER-123"
                return self.tools.check_order_status(order_id)

            elif tool_name == "get_product_info":
                product_id = self._extract_product_id(message) or "PROD-001"
                return self.tools.get_product_info(product_id)

            elif tool_name == "check_account_balance":
                account_id = "ACC-123"  # Would extract from session
                return self.tools.check_account_balance(account_id)

            elif tool_name == "create_support_ticket":
                return self.tools.create_support_ticket(
                    subject=f"Escalation: {context.get('intent')}", description=message
                )

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return None

        return None

    def _extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from message."""
        match = re.search(r"ORDER[-]?\d+", message, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_product_id(self, message: str) -> Optional[str]:
        """Extract product ID from message."""
        match = re.search(r"PROD[-]?\d+", message, re.IGNORECASE)
        return match.group(0) if match else None

    def _generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response using fallback chain."""
        # Try LLM first if available
        if self.llm and self.llm.available:
            response = self.llm.generate_response(message, context)
            if response:
                return response

        # Try fallback provider
        if self.fallback_provider:
            try:
                response = self.fallback_provider.generate_response(message, context)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Fallback provider response generation failed: {e}")

        # Try keyword provider
        if self.keyword_provider:
            try:
                response = self.keyword_provider.generate_response(message, context)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Keyword provider response generation failed: {e}")

        # Fallback: template-based response
        intent = context.get("intent", "general")
        sentiment = context.get("sentiment", 0.0)

        # Empathy prefix for frustrated customers
        prefix = "I understand this is frustrating. " if sentiment < -0.3 else ""

        templates = {
            "password_reset": f"{prefix}I can help you reset your password. You'll receive a secure reset link via email within 5 minutes.",
            "billing": f"{prefix}I'd be happy to help with your billing inquiry. Could you provide your order number so I can review your account?",
            "technical": f"{prefix}I'm sorry you're experiencing a technical issue. Could you describe the error you're seeing?",
            "refund": f"{prefix}I understand you'd like to return this item. I can help initiate a refund for you.",
            "product_info": "Great question! Here's the information about our products and pricing.",
            "order": "Let me check the status of your order for you.",
            "general": f"{prefix}Thank you for reaching out! How can I assist you today?",
        }

        return templates.get(intent, templates["general"])


def create_customer_service_agent() -> EnhancedAgent:
    """Factory function to create agent."""
    return EnhancedAgent()


# ==============================================================================
# Framework Integration: Export goal, nodes, and edges for TUI/runner compatibility
# ==============================================================================
# Import from agent_graph to satisfy framework requirements
goal = None
nodes = []
edges = []

try:
    from agent_graph import goal as _goal, nodes as _nodes, edges as _edges

    goal = _goal
    nodes = _nodes
    edges = _edges
except (ImportError, ModuleNotFoundError):
    try:
        # Fallback: Create minimal definitions for framework compatibility
        from framework.graph import (
            Goal,
            SuccessCriterion,
            Constraint,
        )

        goal = Goal(
            id="customer-service-resolution",
            name="Customer Service Resolution",
            description="Resolve customer inquiries with intelligent classification and empathetic responses",
            success_criteria=[
                SuccessCriterion(
                    id="issue-classification",
                    description="Correctly classify customer issue",
                    metric="classification_accuracy",
                    target=">=0.8",
                    weight=0.4,
                ),
                SuccessCriterion(
                    id="customer-satisfaction",
                    description="Customer is satisfied with the response",
                    metric="sentiment_score",
                    target=">0.5",
                    weight=0.4,
                ),
                SuccessCriterion(
                    id="response-quality",
                    description="Response is helpful and empathetic",
                    metric="response_quality",
                    target=">=0.8",
                    weight=0.2,
                ),
            ],
            constraints=[
                Constraint(
                    id="empathy-required",
                    description="All responses must be empathetic and customer-focused",
                    constraint_type="quality",
                    category="tone",
                ),
                Constraint(
                    id="accuracy-required",
                    description="Classifications must be accurate",
                    constraint_type="quality",
                    category="accuracy",
                ),
            ],
        )
        nodes = []
        edges = []
    except ImportError:
        # Last resort: Create dummy definitions for basic compatibility
        class _DummyGoal:
            id = "customer-service-resolution"
            name = "Customer Service Resolution"
            description = "Resolve customer inquiries with intelligent classification and empathetic responses"

        goal = _DummyGoal()
