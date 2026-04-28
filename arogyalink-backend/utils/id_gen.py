import uuid
import time


def generate_case_id() -> str:
    """Generate a short, readable case ID like AL-20260422-A3F9"""
    date = time.strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:4].upper()
    return f"AL-{date}-{suffix}"
