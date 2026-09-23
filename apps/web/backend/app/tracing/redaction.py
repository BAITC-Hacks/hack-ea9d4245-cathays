import re
def mask(value: str) -> str:
    if len(value) < 5: return "***"
    return value[:1] + "***" + value[-2:]
def redact_text(text: str) -> str:
    text = re.sub(r"\b(?:SQ-(?:OGPO|CASCO|TRVL|PROP|NS|DMS)-\d{6}|CL-\d{6})\b", lambda m: mask(m.group()), text)
    text = re.sub(r"[^\s@]+@[^\s@]+\.[^\s@]+", lambda m: mask(m.group()), text)
    return re.sub(r"\+?\d[\d\s-]{7,}\d", lambda m: mask(m.group()), text)

SENSITIVE = {"phone", "iin", "drivers_iin", "new_driver_iin", "policy_number", "claim_number", "email", "address", "new_value", "full_name", "vehicle_plate", "culprit_vehicle_plate", "location"}

def redact(value, key=""):
    if key in {"preview_id", "trace_id", "conversation_id", "turn_id", "operation_id", "client_turn_id"}:
        return value
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    if key in SENSITIVE:
        if isinstance(value, list): return [mask(str(item)) for item in value]
        return mask(str(value))
    if isinstance(value, dict): return {name: redact(item, name) for name,item in value.items()}
    if isinstance(value, list): return [redact(item) for item in value]
    if isinstance(value, str): return redact_text(value)
    return value
