"""Satisfaction tracking node - tracks customer satisfaction and closes tickets."""


def track_satisfaction_node(context: dict) -> dict:
    """
    Track customer satisfaction and close ticket.

    Args:
        context: Context dictionary containing response and resolution status

    Returns:
        Updated context with satisfaction tracking
    """
    resolved = context.get("resolved", False)

    # Placeholder satisfaction score (in real scenario, would ask customer)
    satisfaction_score = 0.8 if resolved else 0.5

    context["satisfaction_score"] = satisfaction_score
    context["ticket_closed"] = True
    context["status"] = "completed"

    return context
