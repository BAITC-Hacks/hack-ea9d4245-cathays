import re
def mask(value: str) -> str:
    if len(value) < 5: return "***"
    return value[:1] + "***" + value[-2:]
def redact_text(text: str) -> str:
    return re.sub(r"\+?\d[\d\s-]{7,}\d", lambda m: mask(m.group()), text)
