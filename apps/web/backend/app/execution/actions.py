from uuid import uuid4
class ActionError(ValueError):
    def __init__(self,code,message=""):self.code=code;super().__init__(message or code)
class MockActions:
    def __init__(self,snapshot):self.snapshot=snapshot;self.executed={}
    def execute(self,name:str,inputs:dict,idempotency_key:str)->dict:
        if name not in self.snapshot.actions: raise ActionError("invalid_input","unknown action")
        if idempotency_key in self.executed:return self.executed[idempotency_key]
        definition=self.snapshot.actions[name]
        missing=[x for x in definition.get("inputs",[]) if not any(name in inputs and inputs[name] is not None and inputs[name] != "" for name in x.split("|"))]
        if missing:raise ActionError("invalid_input",f"missing {missing[0]}")
        result={"action":name,"status":"completed","outputs":{}}
        if name.startswith("create_") or name in {"renew_policy","book_inspection","book_appointment"}:result["outputs"]["operation_id"]=f"MOCK-{uuid4().hex[:10].upper()}"
        self.executed[idempotency_key]=result;return result
