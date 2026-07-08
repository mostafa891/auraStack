def normalize_email(email: str) -> str:
    """تطهير الفراغات وتوحيد حالة الأحرف للبريد الإلكتروني بنقاء."""
    if not isinstance(email, str):
        return email
    return email.strip().lower()
