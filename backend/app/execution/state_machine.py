from dataclasses import dataclass
from hashlib import sha256
@dataclass
class ActionState:
    state:str; preview_id:str; action:str; inputs:dict; result:dict|None=None
class ConfirmationMachine:
    def __init__(self,actions):self.actions=actions;self.records={}
    def preview(self,cid,action,inputs):
        key=sha256(f"{cid}:{action}:{sorted(inputs.items())}".encode()).hexdigest(); self.records.setdefault(key,ActionState("WAITING_CONFIRMATION",key,action,inputs));return self.records[key]
    def confirm(self,preview_id,affirmative:bool):
        record=self.records[preview_id]
        if record.state=="COMPLETED":return record
        if not affirmative:record.state="CANCELLED";return record
        record.state="EXECUTING";record.result=self.actions.execute(record.action,record.inputs,record.preview_id);record.state="COMPLETED";return record
