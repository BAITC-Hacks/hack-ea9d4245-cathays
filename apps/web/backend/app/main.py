from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StrictBool, model_validator
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware
from copy import deepcopy
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
from .tracing.redaction import redact
from .grounding.responder import respond
from .api.errors import install

snapshot=load_snapshot(settings.dataset_path); validate(snapshot)
router=RouterService(snapshot,OpenAICompatibleClient(settings.base_url,settings.api_key,settings.model),settings.policy_version)
conversations=ConversationStore(); actions=MockActions(snapshot); executor=ScenarioExecutor(snapshot,actions,ConfirmationMachine(actions)); traces={}
app=FastAPI(title="Voice Router",version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["GET","POST"], allow_headers=["Content-Type"])
install(app)
class TurnInput(BaseModel):
    text:str=Field(default="",max_length=4000)
    input_mode:Literal["text"]="text"
    client_turn_id:str=Field(min_length=1,max_length=128,pattern=r"\S")
    preview_id:str|None=Field(default=None,min_length=1,max_length=128)
    confirmed:StrictBool|None=None

    @model_validator(mode="after")
    def valid_turn(self):
        if self.preview_id:
            if self.confirmed is None: raise ValueError("confirmation is required")
        elif self.confirmed is not None:
            raise ValueError("preview_id is required for confirmation")
        elif not self.text.strip():
            raise ValueError("text must not be empty")
        return self
@app.get("/health")
def health(): return {"status":"ok","catalog_version":snapshot.version,"provider_configured":bool(settings.api_key and settings.model and settings.base_url)}
@app.post("/v1/conversations")
def create_conversation():
    c=conversations.create(); return {"conversation_id":c.id,"status":"open"}
@app.post("/v1/conversations/{conversation_id}/turns")
def turn(conversation_id:str, body:TurnInput):
    try: c=conversations.get(conversation_id)
    except KeyError: raise HTTPException(404,"conversation not found")
    with c.lock:
        if body.client_turn_id in c.cache: return c.cache[body.client_turn_id]
        # A preview issued on turn 10 must still be confirmable or cancellable.
        if len(c.turns)>=10 and not body.preview_id:
            raise HTTPException(409,{"code":"conversation_limit","message":"Conversation exchange limit reached. Start a new session."})
        if body.preview_id:
            try: execution=executor.confirm(body.preview_id,body.confirmed,c.id)
            except KeyError: raise HTTPException(404,{"code":"preview_not_found","message":"This action preview is not available in this conversation."}) from None
            record=executor.machine.records[body.preview_id]
            result={"selected":[{"id":record.scenario_id or c.state["active_scenario"] or "SYS_UNCLEAR","confidence":"high","reason":"confirmation"}],"alternatives":[],"language":c.state["language_history"][-1] if c.state["language_history"] else "ru","extracted_slots":{},"continuation":True,"topic_changed":False,"clarification":{"required":False},"metadata":{"catalog_version":snapshot.version,"policy_version":settings.policy_version},"latency_ms":{}}
        else:
            result=router.route(body.text,c.context())
            previous_state=deepcopy(c.state)
            c.update(result)
            try: execution=executor.next_step(c.id,result,c.context())
            except Exception:
                c.state=previous_state
                raise
        turn_id=str(len(c.turns)+1); entry=trace(c.id,turn_id,body.text,result,execution); traces[(c.id,turn_id)]=entry
        response={"conversation_id":c.id,"turn_id":turn_id,"trace_id":entry["trace_id"],"routing":redact(result),"execution":redact(execution),"assistant_message":respond(snapshot,result,execution)}
        c.turns.append(response); c.cache[body.client_turn_id]=response; return response
@app.get("/v1/conversations/{conversation_id}")
def get_conversation(conversation_id:str):
    try: c=conversations.get(conversation_id); return {"conversation_id":c.id,"turns":c.turns,"state":redact(c.context())}
    except KeyError: raise HTTPException(404,"conversation not found")
@app.get("/v1/conversations/{conversation_id}/traces/{turn_id}")
def get_trace(conversation_id:str,turn_id:str):
    if (conversation_id,turn_id) not in traces: raise HTTPException(404,"trace not found")
    return traces[(conversation_id,turn_id)]
