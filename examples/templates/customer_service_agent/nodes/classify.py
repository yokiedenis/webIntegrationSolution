"""Classification node - categorizes customer inquiries."""


def classify_node(context: dict) -> dict:
    """
    Classify customer inquiry type and analyze sentiment.

    Args:
        context: Context dictionary containing inquiry

    Returns:
        Updated context with classification and sentiment
    """
    inquiry = context.get("inquiry", "").lower()

    # Keyword-based classification
    if any(word in inquiry for word in ["return", "refund", "money back"]):
        issue_type = "refunds"
    elif any(
        word in inquiry for word in ["password", "login", "reset", "forgot", "locked"]
    ):
        issue_type = "password_reset"
    elif any(
        word in inquiry for word in ["charge", "bill", "invoice", "payment", "price"]
    ):
        issue_type = "billing"
    elif any(
        word in inquiry for word in ["error", "broken", "not working", "bug", "crash"]
    ):
        issue_type = "technical"
    else:
        issue_type = "general"

    # Simple sentiment analysis
    sentiment = 0.0
    negative_words = ["angry", "frustrated", "terrible", "awful", "broken"]
    positive_words = ["thank", "appreciate", "great", "excellent"]

    if any(word in inquiry for word in negative_words):
        sentiment = -0.7
    elif any(word in inquiry for word in positive_words):
        sentiment = 0.7

    context["issue_type"] = issue_type
    context["sentiment"] = sentiment
    context["classification_method"] = "keyword"
    context["status"] = "classified"

    return context
