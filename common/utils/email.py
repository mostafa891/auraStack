def normalize_email(email: str) -> str:
    """Normalizes and trims whitespace and casing for email addresses."""
    if not isinstance(email, str):
        return email
    return email.strip().lower()
