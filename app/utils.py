def phone_to_int(phone: str) -> int:
    """
    Converts a phone number string to an integer.
    e.g., "050-1234567" → 501234567
    """
    return int(phone.replace("-", ""))


def int_to_phone(i: int) -> str:
    """
    Converts an integer to a phone number string.
    e.g., 501234567 → "050-1234567"
    """
    s = f"{i:010d}"
    return f"{s[:3]}-{s[3:]}"
