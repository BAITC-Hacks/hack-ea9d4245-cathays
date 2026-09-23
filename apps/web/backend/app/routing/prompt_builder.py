from ..dataset.repository import SYSTEM_INTENTS
PROMPT_VERSION="routing-v1"
def build_prompt(snapshot,message,state):
 cards=[]
 for s in snapshot.scenarios.values():
  boundaries="; ".join(f"NOT: {x['condition']} -> {x['use_instead']}" for x in s.get("not_this_if",[]))
  cards.append(f"{s['scenario_id']} | {s['description']} | priority={s['priority']} | {boundaries}")
 return "\n".join(["You are a Saqta Insurance semantic router. The LLM alone selects IDs, never actions/facts.","Compare exclusions and preserve distinct goals; urgent first, otherwise message order.",f"System intents: {', '.join(sorted(SYSTEM_INTENTS))}",f"Relevant state: {state}","Catalog:",*cards,"Return JSON only: {selected:[{id,confidence,reason}],alternatives:[{id,confidence,reason}],language,extracted_slots,continuation,topic_changed,clarification:{required,question?}}.",f"Customer message: {message}"])
