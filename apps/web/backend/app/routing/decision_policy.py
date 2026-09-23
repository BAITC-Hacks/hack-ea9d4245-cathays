from ..dataset.repository import SYSTEM_INTENTS
def apply(result: dict, attempts: int=0) -> dict:
    primary=result["selected"][0]; confidence=primary["confidence"]
    score=confidence if isinstance(confidence,(float,int)) else {"high":.9,"medium":.6,"low":.3}.get(confidence,.3)
    if primary["id"] in SYSTEM_INTENTS: return result
    material=bool(result["alternatives"] and result["alternatives"][0]["confidence"] in ("high", "medium"))
    if score < .75 or material:
        result["selected"]=[{"id":"SYS_UNCLEAR","confidence":"low","reason":"insufficiently distinct eligible scenarios"}]
        result["clarification"]={"required":True,"question":"Это запрос о " + " или ".join(x["id"] for x in result["alternatives"][:2]) + "?"}
        if attempts>=1: result["handoff"]={"required":True,"queue":"operator_general"}
    return result
