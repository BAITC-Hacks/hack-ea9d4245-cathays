from .identity import identify, IdentityError, IDENTIFIERS

class ScenarioExecutor:
 def __init__(self,snapshot,actions,machine):self.snapshot=snapshot;self.actions=actions;self.machine=machine
 def next_step(self,cid,result,context=None):
  self.machine.invalidate(cid)
  sid=result["selected"][0]["id"]
  if result.get("handoff",{}).get("required"):
   return {"mode":"handoff","status":"requested","queue":result["handoff"]["queue"]}
  if not sid.startswith("SC"):return {"mode":"none","status":"not_applicable"}
  scenario=self.snapshot.scenarios[sid]
  inputs={**(context or {}).get("slots",{}),**result["extracted_slots"]}
  handoff=scenario.get("handoff")
  if handoff and handoff.get("when")=="always":
   result["handoff"]={"required":True,"queue":handoff["queue"]}
   return {"mode":"handoff","status":"requested","queue":handoff["queue"]}
  missing=[x for x in scenario["slots"].get("required",[]) if x not in inputs]
  if missing:return {"mode":"collect_slot","status":"waiting","slot":missing[0]}
  if scenario.get("requires_identification"):
   if not any(name in inputs for name in IDENTIFIERS):return {"mode":"collect_slot","status":"waiting","slot":"phone"}
   try: inputs["client_id"]=identify(self.snapshot.backend,inputs)["client_id"]
   except IdentityError as error: return {"mode":"collect_slot","status":"waiting","slot":"phone","error":str(error)}
  if scenario.get("requires_confirmation"):
   action=next((x for x in scenario["actions"] if self.snapshot.actions[x].get("irreversible")),None)
   if not action:return {"mode":"fallback","status":"failed"}
   product={"SC02":"ogpo","SC06":"travel","SC12":"ogpo","SC13":"casco","SC14":"property","SC16":"accident"}.get(sid)
   if product:inputs["product_type"]=product
   for required in self.snapshot.actions[action].get("inputs",[]):
    options=required.split("|")
    if not any(name in inputs for name in options):
     slot=next((name for name in options if name in self.snapshot.slots),None)
     if slot:return {"mode":"collect_slot","status":"waiting","slot":slot}
     return {"mode":"fallback","status":"failed"}
   preview=self.machine.preview(cid,action,inputs,scenario_id=sid)
   return {"mode":"preview","status":preview.state.lower(),"preview_id":preview.preview_id,"action":action}
  return {"mode":"information","status":"complete"}
 def confirm(self,preview_id,affirmative,conversation_id=None):
  state=self.machine.confirm(preview_id,affirmative,conversation_id)
  return {"mode":"execute" if state.state=="COMPLETED" else "cancel","status":state.state.lower(),"preview_id":state.preview_id,"action":state.action,"result":state.result}
