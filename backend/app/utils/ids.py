import secrets


def generate_public_reference_code(prefix: str = "SRM") -> str:
    """
    Generates a short public reference code for anonymous report tracking.
    Example: SRM-8F2KQ1
    """
    token = secrets.token_hex(3).upper()
    return f"{prefix}-{token}"