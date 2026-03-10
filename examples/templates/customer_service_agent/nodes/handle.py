"""Handler node - generates empathetic responses based on issue classification."""


def handle_node(context: dict) -> dict:
    """
    Generate response based on issue type and sentiment.

    Args:
        context: Context containing issue_type, sentiment, and inquiry

    Returns:
        Updated context with agent response
    """
    issue_type = context.get("issue_type", "general")
    sentiment = context.get("sentiment", 0.0)

    # Response templates by issue type
    responses = {
        "password_reset": "I can help you reset your password. I'll send a secure link to your registered email. Please check your inbox (and spam folder) within 5 minutes.",
        "billing": "I understand your billing concern. Could you provide your order number or account email so I can review your account and assist you?",
        "technical": "I'm sorry you're experiencing a technical issue. Could you describe the error you're seeing? That will help me troubleshoot faster.",
        "refunds": "I appreciate you reaching out about a refund. I'd be happy to help. Could you tell me more about what you'd like to return?",
        "general": "Thank you for contacting us! I'm here to help with your inquiry. How can I assist you today?",
    }

    # Get base response
    agent_response = responses.get(issue_type, responses["general"])

    # Add empathy if customer is frustrated
    if sentiment < -0.3:
        empathy_prefix = "I understand this is frustrating. "
        agent_response = empathy_prefix + agent_response

    context["agent_response"] = agent_response
    context["response_method"] = "template"
    context["resolved"] = issue_type != "general"
    context["status"] = "response_generated"

    return context
