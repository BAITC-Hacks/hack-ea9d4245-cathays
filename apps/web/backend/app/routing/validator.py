from ..dataset.repository import DatasetSnapshot, SYSTEM_INTENTS
class RoutingValidationError(ValueError): pass
def validate(raw: dict, snapshot: DatasetSnapshot) -> dict:
    selected=raw.get("selected", raw.get("scenarios", [])); alternatives=raw.get("alternatives", [])
    if not isinstance(selected,list) or not selected: raise RoutingValidationError("empty selected")
    ids=[x.get("id",x.get("scenario_id")) for x in selected]
    valid=set(snapshot.scenarios)|SYSTEM_INTENTS
    if any(x not in valid for x in ids) or len(set(ids))!=len(ids): raise RoutingValidationError("invalid or duplicate selected id")
    alt_ids=[x.get("id",x.get("scenario_id")) for x in alternatives]
    if any(x not in valid for x in alt_ids) or set(ids)&set(alt_ids): raise RoutingValidationError("invalid alternatives")
    if any(x in SYSTEM_INTENTS for x in ids) and len(ids)>1: raise RoutingValidationError("system intent cannot mix with business intent")
    slots=raw.get("extracted_slots",raw.get("slots",{}))
    if any(k not in snapshot.slots for k in slots): raise RoutingValidationError("unknown slot")
    return {"selected":[{"id":i,"confidence":selected[n].get("confidence","medium"),"reason":selected[n].get("reason","")} for n,i in enumerate(ids)],"alternatives":[{"id":i,"confidence":alternatives[n].get("confidence","low"),"reason":alternatives[n].get("reason","")} for n,i in enumerate(alt_ids)],"language":raw.get("language","mixed"),"extracted_slots":slots,"continuation":bool(raw.get("continuation",raw.get("is_continuation",False))),"topic_changed":bool(raw.get("topic_changed",False)),"clarification":raw.get("clarification",{"required":False})}
