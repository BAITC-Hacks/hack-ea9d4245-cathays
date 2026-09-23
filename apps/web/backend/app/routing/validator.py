from ..dataset.repository import DatasetSnapshot, SYSTEM_INTENTS
from ..execution.slots import normalize, SlotError
from math import isfinite
class RoutingValidationError(ValueError): pass

def candidates(items, valid, default):
    if not isinstance(items, list): raise RoutingValidationError("candidates must be a list")
    parsed = []
    for item in items:
        if not isinstance(item, dict): raise RoutingValidationError("candidate must be an object")
        sid = item.get("id", item.get("scenario_id"))
        if not isinstance(sid, str) or sid not in valid: raise RoutingValidationError("invalid scenario id")
        confidence = item.get("confidence", default)
        if isinstance(confidence, bool) or not (
            isinstance(confidence, str) and confidence in {"high", "medium", "low"}
            or isinstance(confidence, (int, float)) and isfinite(confidence) and 0 <= confidence <= 1
        ): raise RoutingValidationError("invalid confidence")
        reason = item.get("reason", "")
        if not isinstance(reason, str): raise RoutingValidationError("reason must be text")
        parsed.append({"id": sid, "confidence": confidence, "reason": reason})
    if len({item["id"] for item in parsed}) != len(parsed): raise RoutingValidationError("duplicate scenario id")
    return parsed
def validate(raw: dict, snapshot: DatasetSnapshot) -> dict:
    if not isinstance(raw, dict): raise RoutingValidationError("routing result must be an object")
    valid=set(snapshot.scenarios)|SYSTEM_INTENTS
    selected=candidates(raw.get("selected", raw.get("scenarios", [])), valid, "medium")
    alternatives=candidates(raw.get("alternatives", []), valid, "low")
    if not selected: raise RoutingValidationError("empty selected")
    ids=[item["id"] for item in selected]
    if set(ids)&{item["id"] for item in alternatives}: raise RoutingValidationError("invalid alternatives")
    if any(x in SYSTEM_INTENTS for x in ids) and len(ids)>1: raise RoutingValidationError("system intent cannot mix with business intent")
    slots=raw.get("extracted_slots",raw.get("slots",{}))
    if not isinstance(slots, dict): raise RoutingValidationError("slots must be an object")
    if any(k not in snapshot.slots for k in slots): raise RoutingValidationError("unknown slot")
    try: slots={name: normalize(name, value, snapshot.slots[name], snapshot.as_of_date) for name,value in slots.items()}
    except SlotError as error: raise RoutingValidationError(str(error)) from None
    language=raw.get("language", "mixed")
    if language not in ("ru", "kk", "mixed"): raise RoutingValidationError("invalid language")
    continuation=raw.get("continuation", raw.get("is_continuation", False))
    changed=raw.get("topic_changed", False)
    clarification=raw.get("clarification", {"required": False})
    if not isinstance(continuation, bool) or not isinstance(changed, bool): raise RoutingValidationError("state flags must be booleans")
    if not isinstance(clarification, dict) or not isinstance(clarification.get("required", False), bool): raise RoutingValidationError("invalid clarification")
    question=clarification.get("question")
    if question is not None and not isinstance(question, str): raise RoutingValidationError("clarification question must be text")
    return {"selected":selected,"alternatives":alternatives,"language":language,"extracted_slots":slots,"continuation":continuation,"topic_changed":changed,"clarification":{"required":clarification.get("required",False),"question":question}}
