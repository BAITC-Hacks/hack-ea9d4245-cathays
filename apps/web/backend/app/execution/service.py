class ScenarioExecutor:
 def __init__(self,snapshot,actions,machine):self.snapshot=snapshot;self.actions=actions;self.machine=machine
 def next_step(self,cid,result):
  sid=result["selected"][0]["id"]
  if not sid.startswith("SC"):return {"mode":"none","status":"not_applicable"}
  scenario=self.snapshot.scenarios[sid];missing=[x for x in scenario["slots"].get("required",[]) if x not in result["extracted_slots"]]
  if missing:return {"mode":"collect_slot","status":"waiting","slot":missing[0]}
  if scenario.get("requires_confirmation"):
   action=next((x for x in scenario["actions"] if self.snapshot.actions[x].get("irreversible")),None)
   if not action:return {"mode":"fallback","status":"failed"}
   preview=self.machine.preview(cid,action,result["extracted_slots"])
   return {"mode":"preview","status":preview.state.lower(),"preview_id":preview.preview_id,"action":action}
  return {"mode":"information","status":"complete"}
 def confirm(self,preview_id,affirmative):
  state=self.machine.confirm(preview_id,affirmative)
  return {"mode":"execute" if state.state=="COMPLETED" else "cancel","status":state.state.lower(),"preview_id":state.preview_id,"action":state.action,"result":state.result}
