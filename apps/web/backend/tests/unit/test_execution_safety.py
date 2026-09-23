from app.execution.state_machine import ConfirmationMachine

class Actions:
    def __init__(self): self.calls=0
    def execute(self,*args): self.calls+=1; return {"status":"completed"}

def test_preview_requires_affirmation_and_is_idempotent():
    actions=Actions(); machine=ConfirmationMachine(actions); preview=machine.preview("c","update_contact",{"phone":"+77000000000"})
    assert machine.confirm(preview.preview_id,False).state=="CANCELLED" and actions.calls==0
    preview=machine.preview("c2","update_contact",{"phone":"+77000000000"})
    assert machine.confirm(preview.preview_id,True).state=="COMPLETED"
    machine.confirm(preview.preview_id,True); assert actions.calls==1
