import re


def to_e164(phone: str, default_country_code: str = "91") -> str:
    """Normalize Indian phone numbers to E.164 format (+91XXXXXXXXXX)"""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    if len(digits) == 10:
        return f"+{default_country_code}{digits}"
    if phone.startswith("+"):
        return phone
    return f"+{digits}"


def is_valid_indian_mobile(phone: str) -> bool:
    e164 = to_e164(phone)
    return bool(re.match(r'^\+91[6-9]\d{9}$', e164))
