from hashlib import sha256
class ScenarioExecutor:
 def __init__(self,snapshot):self.snapshot=snapshot;self.records={}
 def next_step(self,cid,result):
  sid=result["selected"][0]["id"]
  if not sid.startswith("SC"):return {"mode":"none","status":"not_applicable"}
  scenario=self.snapshot.scenarios[sid];missing=[x for x in scenario["slots"].get("required",[]) if x not in result["extracted_slots"]]
  if missing:return {"mode":"collect_slot","status":"waiting","slot":missing[0]}
  if scenario.get("requires_confirmation"):
   key=sha256(f"{cid}:{sid}:{result['extracted_slots']}".encode()).hexdigest();self.records.setdefault(key,{"mode":"preview","status":"waiting_confirmation"});return {**self.records[key],"idempotency_key":key}
  return {"mode":"information","status":"complete"}
