from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .settings import settings
from .dataset.repository import load_snapshot
from .dataset.validator import validate
from .routing.provider_client import OpenAICompatibleClient
from .routing.service import RouterService
from .dialogue.service import ConversationStore
from .execution.service import ScenarioExecutor
from .execution.actions import MockActions
from .execution.state_machine import ConfirmationMachine
from .tracing.service import trace
from .grounding.responder import respond
from .api.errors import install

snapshot=load_snapshot(settings.dataset_path); validate(snapshot)
router=RouterService(snapshot,OpenAICompatibleClient(settings.base_url,settings.api_key,settings.model),settings.policy_version)
conversations=ConversationStore(); actions=MockActions(snapshot); executor=ScenarioExecutor(snapshot,actions,ConfirmationMachine(actions)); traces={}
app=FastAPI(title="Voice Router",version="0.1.0")
install(app)
class TurnInput(BaseModel):
    text:str=""; input_mode:str="text"; client_turn_id:str; preview_id:str|None=None; confirmed:bool|None=None
@app.get("/health")
def health(): return {"status":"ok","catalog_version":snapshot.version}
@app.post("/v1/conversations")
def create_conversation():
    c=conversations.create(); return {"conversation_id":c.id,"status":"open"}
@app.post("/v1/conversations/{conversation_id}/turns")
def turn(conversation_id:str, body:TurnInput):
    try: c=conversations.get(conversation_id)
    except KeyError: raise HTTPException(404,"conversation not found")
    if body.client_turn_id in c.cache: return c.cache[body.client_turn_id]
    if len(c.turns)>=10: raise HTTPException(409,"conversation exchange limit reached")
    if body.preview_id:
        if body.confirmed is None: raise HTTPException(422,"confirmation is required")
        execution=executor.confirm(body.preview_id,body.confirmed)
        result={"selected":[{"id":c.state["active_scenario"] or "SYS_UNCLEAR","confidence":"high","reason":"confirmation"}],"alternatives":[],"language":c.state["language_history"][-1] if c.state["language_history"] else "ru","extracted_slots":{},"continuation":True,"topic_changed":False,"clarification":{"required":False},"metadata":{"catalog_version":snapshot.version,"policy_version":settings.policy_version},"latency_ms":{}}
    else:
        result=router.route(body.text,c.context()); execution=executor.next_step(c.id,result); c.update(result)
    turn_id=str(len(c.turns)+1); entry=trace(c.id,turn_id,body.text,result,execution); traces[(c.id,turn_id)]=entry
    response={"conversation_id":c.id,"turn_id":turn_id,"trace_id":entry["trace_id"],"routing":result,"execution":execution,"assistant_message":respond(snapshot,result,execution)}
    c.turns.append(response); c.cache[body.client_turn_id]=response; return response
@app.get("/v1/conversations/{conversation_id}")
def get_conversation(conversation_id:str):
    try: c=conversations.get(conversation_id); return {"conversation_id":c.id,"turns":c.turns,"state":c.context()}
    except KeyError: raise HTTPException(404,"conversation not found")
@app.get("/v1/conversations/{conversation_id}/traces/{turn_id}")
def get_trace(conversation_id:str,turn_id:str):
    if (conversation_id,turn_id) not in traces: raise HTTPException(404,"trace not found")
    return traces[(conversation_id,turn_id)]
