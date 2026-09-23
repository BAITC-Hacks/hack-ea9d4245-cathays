from dataclasses import dataclass
from copy import deepcopy
from threading import RLock
from uuid import uuid4
from .actions import ActionError
@dataclass
class ActionState:
    state:str; preview_id:str; action:str; inputs:dict; result:dict|None=None; conversation_id:str=""; scenario_id:str|None=None
class ConfirmationMachine:
    def __init__(self,actions):self.actions=actions;self.records={};self.lock=RLock()
    def invalidate(self, cid):
        with self.lock:
            for record in self.records.values():
                if record.conversation_id == cid and record.state == "WAITING_CONFIRMATION":
                    record.state = "CANCELLED"
    def preview(self,cid,action,inputs,scenario_id=None):
        with self.lock:
            self.invalidate(cid)
            key=uuid4().hex
            record=ActionState("WAITING_CONFIRMATION",key,action,deepcopy(inputs),conversation_id=cid,scenario_id=scenario_id)
            self.records[key]=record
            return record
    def confirm(self,preview_id,affirmative:bool,conversation_id=None):
        with self.lock:
            record=self.records[preview_id]
            if conversation_id is not None and record.conversation_id != conversation_id:
                raise KeyError(preview_id)
            if record.state in {"COMPLETED", "CANCELLED"}:return record
            if record.state != "WAITING_CONFIRMATION":
                raise ActionError("invalid_input", "Create a new preview before retrying the action")
            if not affirmative:record.state="CANCELLED";return record
            record.state="EXECUTING"
            try:
                record.result=self.actions.execute(record.action,record.inputs,record.preview_id)
            except Exception:
                record.state="FAILED"
                raise
            record.state="COMPLETED"
            return record
