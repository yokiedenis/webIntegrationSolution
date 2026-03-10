"""Intake node - receives and understands customer inquiries."""


def intake_node(context: dict) -> dict:
    """
    Receives and validates customer inquiry.

    Args:
        context: Context dictionary containing customer_message

    Returns:
        Updated context with validated inquiry
    """
    customer_message = context.get("customer_message", "")

    if not customer_message:
        context["error"] = "No customer message provided"
        context["status"] = "error"
        return context

    context["inquiry"] = customer_message
    context["status"] = "inquiry_received"
    context["customer_id"] = context.get("customer_id", "unknown")
    context["session_id"] = context.get("session_id", "default")

    return context
