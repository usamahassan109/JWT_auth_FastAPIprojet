import secrets  # ✅ YE LINE ADD KAREIN

def unique_string(byte: int = 8) -> str:
    return secrets.token_urlsafe(byte)