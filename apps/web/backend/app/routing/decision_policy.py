from ..dataset.repository import SYSTEM_INTENTS

def confidence_score(value):
    return float(value) if isinstance(value, (int, float)) else {"high":.9,"medium":.6,"low":.3}.get(value,.3)
def apply(result: dict, attempts: int=0) -> dict:
    primary=result["selected"][0]; confidence=primary["confidence"]
    score=confidence_score(confidence)
    if primary["id"] in SYSTEM_INTENTS:
        if primary["id"] == "SYS_UNCLEAR" and attempts >= 1:
            result["handoff"]={"required":True,"queue":"operator_general"}
        return result
    material=any(confidence_score(item["confidence"]) >= .6 for item in result["alternatives"])
    if score < .75 or material:
        result["alternatives"]=result["selected"] + result["alternatives"]
        result["selected"]=[{"id":"SYS_UNCLEAR","confidence":"low","reason":"insufficiently distinct eligible scenarios"}]
        question = result.get("clarification", {}).get("question")
        result["clarification"]={"required":True,"question":question or ("Қай сақтандыру туралы және не істегіңіз келетінін нақтылаңызшы." if result.get("language")=="kk" else "Уточните, пожалуйста, о какой страховке идёт речь и что вы хотите сделать?")}
        if attempts>=1: result["handoff"]={"required":True,"queue":"operator_general"}
    return result
