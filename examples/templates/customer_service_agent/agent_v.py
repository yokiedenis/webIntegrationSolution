"""Customer Service Agent implementation with NLP and LLM capabilities."""

import json
import logging
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Task:
    """Task definition for the agent."""

    def __init__(self, id, name, description, agent=None):
        self.id = id
        self.name = name
        self.description = description
        self.agent = agent


class Agent:
    """
    Enhanced Customer Service Agent with NLP capabilities.

    Features:
    - LLM-driven intent classification (falls back to keyword matching)
    - Sentiment analysis for customer satisfaction
    - Context-aware response generation
    - Graceful degradation if LLM unavailable
    """

    def __init__(self, name, description, model, llm_provider=None):
        self.name = name
        self.description = description
        self.model = model
        self.llm_provider = llm_provider
        self.tasks: List[Task] = []

        # Fallback keyword-based classifiers
        self.faq_keywords = {
            "password_reset": [
                "password",
                "forgot",
                "reset",
                "locked",
                "can't login",
                "cannot login",
            ],
            "billing": [
                "charge",
                "invoice",
                "payment",
                "bill",
                "price",
                "subscription",
                "cost",
            ],
            "technical": [
                "error",
                "bug",
                "crash",
                "technical",
                "not working",
                "broken",
                "doesn't work",
            ],
            "refunds": [
                "refund",
                "return",
                "money back",
                "reimbursement",
                "cancel",
                "refund request",
            ],
        }

    def add_task(self, task, depends_on=None):
        """Add task to agent."""
        self.tasks.append(task)

    def _classify_with_llm(self, message: str) -> tuple[str | None, float]:
        """
        Classify message intent using LLM (with sentiment analysis).
        Returns (issue_type, sentiment_score) where sentiment_score is -1.0 to 1.0
        """
        if not self.llm_provider:
            return None, 0.0

        try:
            classification_prompt = f"""Analyze this customer service message and classify it.

Message: "{message}"

Respond in JSON format with:
{{"issue_type": "password_reset"|"billing"|"technical"|"refunds"|"general", "sentiment": -1.0 to 1.0, "confidence": 0.0 to 1.0}}

Only respond with valid JSON, no other text."""

            response = self.llm_provider.complete(
                messages=[{"role": "user", "content": classification_prompt}],
                system="You are a customer service intent classifier. Respond only with valid JSON.",
                max_tokens=200,
            )

            result = json.loads(response.content.strip())
            issue_type = result.get("issue_type", "general")
            sentiment = result.get("sentiment", 0.0)
            confidence = result.get("confidence", 0.5)

            logger.debug(
                f"LLM classification: {issue_type} (sentiment={sentiment}, confidence={confidence})"
            )
            return issue_type, sentiment

        except Exception as e:
            logger.warning(
                f"LLM classification failed: {e}, falling back to keyword matching"
            )
            return None, 0.0

    def _classify_with_keywords(self, message: str) -> str:
        """Fallback: classify using keyword matching."""
        message_lower = message.lower()
        for category, keywords in self.faq_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        return "general"

    def _generate_response_with_llm(
        self, message: str, issue_type: str, sentiment: float
    ) -> str | None:
        """Generate contextual response using LLM."""
        if not self.llm_provider:
            return None

        try:
            sentiment_note = (
                "The customer seems frustrated."
                if sentiment < -0.3
                else "The customer seems happy."
                if sentiment > 0.5
                else "The customer is neutral."
            )

            response_prompt = f"""You are a professional, empathetic customer service agent.

Customer Message: "{message}"
Issue Type: {issue_type}
Sentiment: {sentiment_note}

Provide a brief, helpful response (2-3 sentences max) that:
1. Acknowledges the customer's concern
2. Shows empathy if they're frustrated
3. Offers next steps or a solution

Keep the tone professional and friendly."""

            response = self.llm_provider.complete(
                messages=[{"role": "user", "content": response_prompt}],
                system="You are an expert customer service representative. Provide concise, empathetic, helpful responses.",
                max_tokens=300,
            )

            return response.content.strip()

        except Exception as e:
            logger.warning(f"LLM response generation failed: {e}")
            return None

    def _get_fallback_response(self, issue_type: str, message: str) -> str:
        """Fallback responses when LLM is unavailable."""
        responses = {
            "password_reset": "I can help you reset your password. I'll send a secure link to your registered email. Please check your inbox (and spam folder) within 5 minutes.",
            "billing": "I understand your billing concern. Could you provide your order number or account email so I can review your account and assist you?",
            "technical": "I'm sorry you're experiencing a technical issue. Could you describe the error you're seeing? That will help me troubleshoot faster.",
            "refunds": "I appreciate you reaching out about a refund. I'd be happy to help. Could you tell me more about what you'd like to return?",
            "general": "Thank you for contacting us! I'm here to help with your inquiry. How can I assist you today?",
        }
        return responses.get(issue_type, responses["general"])

    def invoke(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer inquiry using NLP and LLM with intelligent fallbacks.

        Args:
            data: {
                'customer_message': str,
                'customer_id': str (optional),
                'session_id': str (optional)
            }

        Returns:
            {
                'agent_response': str,
                'issue_type': str,
                'resolved': bool,
                'sentiment': float,
                'customer_id': str,
                'session_id': str,
                'used_llm': bool
            }
        """
        message = data.get("customer_message", "")
        customer_id = data.get("customer_id", "unknown")
        session_id = data.get("session_id", "default")

        if not message:
            return {
                "agent_response": "I didn't receive your message. Could you please provide more details about how I can help?",
                "issue_type": "general",
                "resolved": False,
                "sentiment": 0.0,
                "customer_id": customer_id,
                "session_id": session_id,
                "used_llm": False,
                "error": "No message provided",
            }

        # Step 1: Try LLM-based classification and sentiment analysis
        issue_type, sentiment = self._classify_with_llm(message)
        used_llm_classify = issue_type is not None

        # Fallback to keyword matching if LLM failed
        if not used_llm_classify:
            issue_type = self._classify_with_keywords(message)

        # Step 2: Generate response
        agent_response = None
        used_llm_response = False

        if self.llm_provider:
            agent_response = self._generate_response_with_llm(
                message, issue_type, sentiment
            )
            used_llm_response = agent_response is not None

        # Fallback to template response
        if not agent_response:
            agent_response = self._get_fallback_response(issue_type, message)

        return {
            "agent_response": agent_response,
            "issue_type": issue_type,
            "resolved": issue_type != "general",  # General issues may need escalation
            "sentiment": sentiment,
            "customer_id": customer_id,
            "session_id": session_id,
            "used_llm": used_llm_classify or used_llm_response,
            "classification_method": "llm" if used_llm_classify else "keyword",
            "response_method": "llm" if used_llm_response else "template",
        }


def create_customer_service_agent() -> Agent:
    """Create and configure the customer service agent with LLM capabilities."""
    import os

    # Get model from environment or use default
    model_name = os.getenv("AGENT_MODEL", "groq/llama-3.1-70b-versatile")

    # Try to initialize LLM provider (optional - agent works without it)
    llm_provider = None
    try:
        # Try direct litellm first
        import litellm

        litellm.api_key = os.getenv("GROQ_API_KEY")

        class SimpleLLMProvider:
            def __init__(self, model):
                self.model = model

            def complete(self, messages, system=None, max_tokens=200):
                """Call LLM via litellm."""
                try:
                    response = litellm.completion(
                        model=self.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=float(os.getenv("AGENT_TEMPERATURE", 0.7)),
                    )

                    class Response:
                        def __init__(self, content):
                            self.content = content

                    # Extract content from response with safe attribute access
                    content: str | None = None
                    try:
                        # Try standard litellm response format
                        choices = getattr(response, "choices", None)  # type: ignore
                        if choices:
                            choice = choices[0]
                            message = getattr(choice, "message", None)
                            if message:
                                content = getattr(message, "content", None)
                    except (AttributeError, IndexError, TypeError):
                        pass

                    if not content:
                        # Fallback for string responses
                        content = str(response) if response else None

                    return Response(content or "")
                except Exception as e:
                    raise Exception(f"LLM API error: {e}")

        llm_provider = SimpleLLMProvider(model_name)
        logger.info(f"LLM provider initialized with {model_name}")
    except ImportError:
        logger.warning("litellm not available, using keyword-based classification")
    except Exception as e:
        logger.warning(
            f"Failed to initialize LLM provider: {e}, using keyword-based fallback"
        )

    agent = Agent(
        name="customer_service_agent",
        description="Intelligent customer service agent with NLP and LLM capabilities",
        model=model_name,
        llm_provider=llm_provider,
    )

    # Add core tasks (for multi-step workflows)
    intake_task = Task(
        id="intake",
        name="Receive Customer Inquiry",
        description="Receive and understand the customer's inquiry",
        agent=agent,
    )

    classify_task = Task(
        id="classify",
        name="Classify Issue Type",
        description="Classify the customer inquiry using NLP and LLM",
        agent=agent,
    )

    handle_task = Task(
        id="handle",
        name="Handle Customer Request",
        description="Generate context-aware response based on sentiment and issue type",
        agent=agent,
    )

    track_task = Task(
        id="track",
        name="Track Satisfaction",
        description="Monitor sentiment and track customer satisfaction",
        agent=agent,
    )

    # Add dependencies for workflow orchestration
    agent.add_task(intake_task)
    agent.add_task(classify_task, depends_on=[intake_task])
    agent.add_task(handle_task, depends_on=[classify_task])
    agent.add_task(track_task, depends_on=[handle_task])

    return agent


if __name__ == "__main__":
    agent = create_customer_service_agent()
    print(f"Created agent: {agent.name}")
    print(f"Tasks: {len(agent.tasks)}")
