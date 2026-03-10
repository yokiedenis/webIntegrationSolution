"""Keyword-based LLM provider for fallback scenarios."""

import re
from typing import Dict, Any


class KeywordLLMProvider:
    """Lightweight keyword-based provider that doesn't require external API."""

    def __init__(self):
        """Initialize keyword-based provider."""
        self.name = "keyword"
        self.available = True

        # Intent keywords
        self.intent_keywords = {
            "password_reset": [
                "password",
                "forgot",
                "reset",
                "locked",
                "login",
                "access",
                "unlock",
            ],
            "billing": [
                "charge",
                "invoice",
                "payment",
                "bill",
                "refund",
                "cancel",
                "subscription",
                "price",
            ],
            "technical": [
                "error",
                "bug",
                "crash",
                "not working",
                "broken",
                "issue",
                "problem",
                "fail",
            ],
            "refund": [
                "refund",
                "return",
                "money back",
                "reimbursement",
                "reverse",
                "undo",
            ],
            "product_info": [
                "price",
                "feature",
                "plan",
                "product",
                "subscription",
                "details",
                "info",
            ],
            "order": ["order", "tracking", "delivery", "shipped", "status", "when"],
            "escalation": ["speak", "agent", "manager", "human", "escalate", "urgent"],
        }

        # Sentiment indicators
        self.negative_words = {
            "very": 0.5,
            "extremely": 0.7,
            "absolutely": 0.7,
            "angry": 1.0,
            "frustrated": 1.0,
            "upset": 0.9,
            "terrible": 1.0,
            "awful": 1.0,
            "bad": 0.8,
            "hate": 1.0,
            "useless": 0.9,
            "ridiculous": 0.9,
            "stupid": 0.9,
            "waste": 0.8,
            "disappointing": 0.8,
            "unacceptable": 0.9,
        }

        self.positive_words = {
            "thanks": 0.7,
            "appreciate": 0.8,
            "great": 0.9,
            "excellent": 1.0,
            "love": 1.0,
            "happy": 0.9,
            "pleased": 0.8,
            "wonderful": 0.9,
            "fantastic": 0.95,
            "perfect": 0.95,
            "amazing": 0.9,
            "helpful": 0.8,
        }

    def classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify intent using keywords."""
        msg_lower = message.lower()

        # Find matching intents
        matched_intents = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in msg_lower)
            if score > 0:
                matched_intents[intent] = score

        if not matched_intents:
            intent = "general"
            confidence = 0.3
        else:
            intent = max(matched_intents.keys(), key=lambda k: matched_intents[k])
            confidence = min(0.95, matched_intents[intent] / 10.0)

        # Analyze sentiment
        sentiment = self._analyze_sentiment(msg_lower)

        # Determine urgency
        urgency = "high" if sentiment < -0.5 else "low" if sentiment > 0.5 else "medium"

        # Check if tool is needed
        requires_tool = intent in [
            "password_reset",
            "refund",
            "order",
            "product_info",
            "technical",
            "escalation",
        ]

        return {
            "intent": intent,
            "sentiment": sentiment,
            "urgency": urgency,
            "confidence": confidence,
            "requires_tool": requires_tool,
            "tool_name": self._map_intent_to_tool(intent),
            "method": "keyword",
        }

    def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Generate response based on intent and sentiment."""
        intent = context.get("intent", "general")
        sentiment = context.get("sentiment", 0.0)

        # Build empathy prefix
        prefix = ""
        if sentiment < -0.5:
            prefix = (
                "I understand this is very frustrating, and I sincerely apologize. "
            )
        elif sentiment < -0.2:
            prefix = "I understand this is frustrating. "

        # Response templates
        templates = {
            "password_reset": "I can help you reset your password securely. You'll receive a reset link via email within 5 minutes that expires after 24 hours.",
            "billing": "I'd be happy to help with your billing inquiry. Could you provide your order number so I can review your account details?",
            "technical": "I'm sorry you're experiencing a technical issue. Could you describe the error you're seeing? That will help me troubleshoot faster.",
            "refund": "I understand you'd like to return this item. I can help initiate a refund for you. May I ask the reason for the return?",
            "product_info": "I'd be happy to provide information about our products and pricing. Which plan are you interested in learning more about?",
            "order": "Let me check the status of your order for you. I can provide tracking information and estimated delivery date.",
            "escalation": "I appreciate you reaching out. For urgent matters, I can connect you with our support team immediately.",
            "general": "Thank you for reaching out! How can I assist you today?",
        }

        base_response = templates.get(intent, templates["general"])
        return prefix + base_response

    def _analyze_sentiment(self, msg_lower: str) -> float:
        """Analyze sentiment of message."""
        neg_score = 0.0
        pos_score = 0.0

        # Check negative words with multipliers for intensifiers
        intensifiers = ["very", "extremely", "absolutely"]
        for word, weight in self.negative_words.items():
            count = msg_lower.count(word)
            if count > 0:
                # Check for intensifiers
                multiplier = 1.0
                for intensifier in intensifiers:
                    if intensifier in msg_lower:
                        multiplier = 1.5
                        break
                neg_score += count * weight * multiplier

        # Check positive words
        for word, weight in self.positive_words.items():
            count = msg_lower.count(word)
            if count > 0:
                pos_score += count * weight

        # Calculate normalized sentiment
        total = neg_score + pos_score
        if total == 0:
            return 0.0

        sentiment = (pos_score - neg_score) / total
        return max(-1.0, min(1.0, sentiment))

    def _map_intent_to_tool(self, intent: str) -> str:
        """Map intent to tool name."""
        mapping = {
            "password_reset": "reset_password",
            "refund": "initiate_refund",
            "order": "check_order_status",
            "product_info": "get_product_info",
            "billing": "check_account_balance",
            "technical": "create_support_ticket",
            "escalation": "create_support_ticket",
        }
        return mapping.get(intent, "none")

    def extract_parameters(self, message: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from message based on intent."""
        msg_lower = message.lower()
        params = {}

        # Extract order ID
        order_match = re.search(r"order[#-]?(\d+|\w+)", msg_lower)
        if order_match:
            params["order_id"] = order_match.group(0).upper()

        # Extract email
        email_match = re.search(r"[\w.-]+@[\w.-]+\.\w+", message)
        if email_match:
            params["email"] = email_match.group(0)

        # Extract product ID
        product_match = re.search(r"prod[uct]*[#-]?(\d+|\w+)", msg_lower)
        if product_match:
            params["product_id"] = product_match.group(0).upper()

        return params
