from .triage import triage
from .prompt_builder import build_prompt, PROMPT_VERSION
from .validator import validate, RoutingValidationError
from .decision_policy import apply
from ..tracing.timers import Timers

class RouterService:
    def __init__(self,snapshot,client,policy_version="uncertainty-v1"): self.snapshot,self.client,self.policy_version=snapshot,client,policy_version
    def route(self,message,state):
        timers=Timers(); info=triage(message)
        with timers.measure("triage"): pass
        prompt=build_prompt(self.snapshot,message,state)
        try:
            with timers.measure("routing"): raw=self.client.route(prompt)
            result=validate(raw,self.snapshot)
        except (RoutingValidationError, RuntimeError, ValueError) as e:
            timers.fail("routing"); result={"selected":[{"id":"SYS_UNCLEAR","confidence":"low","reason":"routing unavailable or invalid"}],"alternatives":[],"language":info["language"],"extracted_slots":{},"continuation":False,"topic_changed":False,"clarification":{"required":True,"question":"Уточните, пожалуйста, какой вопрос по страхованию?"},"fallback":{"active":True,"reason":str(e)}}
        result=apply(result,state.get("clarification_attempts",0)); result["metadata"]={"catalog_version":self.snapshot.version,"snapshot_date":self.snapshot.as_of_date,"prompt_version":PROMPT_VERSION,"policy_version":self.policy_version}; result["latency_ms"]=timers.result(); return result
