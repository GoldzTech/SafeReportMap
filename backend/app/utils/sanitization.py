import re


EMAIL_PATTERN = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[\s-]?)?(\(?\d{2,3}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def sanitize_text(text: str) -> str:
    """
    Minimal PII sanitization for MVP.
    This is intentionally conservative and can be improved later
    with named-entity recognition or dedicated PII detection.
    """
    sanitized = text.strip()
    sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
    sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    sanitized = URL_PATTERN.sub("[REDACTED_URL]", sanitized)
    return sanitized