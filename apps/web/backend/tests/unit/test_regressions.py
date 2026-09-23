from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from io import BytesIO
from urllib.error import HTTPError, URLError
import json
import pytest
from app.settings import Settings, ROOT
from app.dataset.repository import load_snapshot
from app.execution.identity import identify, IdentityError
from app.execution.state_machine import ConfirmationMachine
from app.execution.slots import normalize, SlotError
from app.execution.actions import MockActions
from app.dialogue.service import Conversation
from app.routing.validator import validate, RoutingValidationError
from app.routing.provider_client import OpenAICompatibleClient
from app.routing.decision_policy import apply
from app.tracing.redaction import redact

@pytest.fixture
def snapshot():
    return load_snapshot(ROOT / "voice_router_dataset/case_2/voice_router_dataset")

def test_dataset_path_is_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for configured in ("", "voice_router_dataset/case_2/voice_router_dataset", "../voice_router_dataset/case_2/voice_router_dataset"):
        monkeypatch.setenv("VOICE_ROUTER_DATASET_PATH", configured)
        assert (Settings().dataset_path / "scenarios.json").is_file()

def test_standard_openai_key_is_supported_without_printing_it(monkeypatch):
    monkeypatch.setenv("VOICE_ROUTER_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    assert Settings().api_key == "test-secret"
    assert "test-secret" not in repr(Settings())

@pytest.mark.parametrize("raw", [None, [], {"selected": [None]}, {"selected": [{"id": []}]}, {"selected": [{"id":"SC01", "confidence": {}}]}, {"selected": [{"id":"SC01", "confidence": 4}]}, {"selected": [{"id":"SC01"}], "alternatives": None}, {"selected": [{"id":"SC01"}], "slots": []}, {"selected": [{"id":"SC01"}], "clarification": None}, {"selected": [{"id":"SC01"}], "continuation": "false"}])
def test_malformed_routing_is_rejected_without_type_errors(snapshot, raw):
    with pytest.raises(RoutingValidationError): validate(raw, snapshot)

def test_normalizes_typed_slots(snapshot):
    values={"phone":"8 (701) 000-00-01", "injured":False, "drivers_iin":["850314300121"], "preferred_date":"tomorrow"}
    result=validate({"selected":[{"id":"SC01","confidence":"high"}],"slots":values},snapshot)
    assert result["extracted_slots"] == {"phone":"+77010000001","injured":False,"drivers_iin":["850314300121"],"preferred_date":"2026-10-02"}

@pytest.mark.parametrize("name,value", [("phone","+17010000001"),("car_year","20.25"),("car_value","-100"),("preferred_date","2026-02-31"),("iin",None),("drivers_iin",[])])
def test_invalid_slots_are_not_silently_changed(snapshot,name,value):
    with pytest.raises(SlotError):normalize(name,value,snapshot.slots[name],snapshot.as_of_date)

def test_identity_resolves_policies_and_claims_and_rejects_conflicts(snapshot):
    assert identify(snapshot.backend,{"policy_number":"SQ-OGPO-104501"})["client_id"] == "C001"
    assert identify(snapshot.backend,{"claim_number":"CL-500198"})["client_id"] == "C001"
    with pytest.raises(IdentityError):identify(snapshot.backend,{"phone":"+77010000001","iin":"920607400233"})
    with pytest.raises(IdentityError):identify(snapshot.backend,{"phone":"+77010000001","iin":"000000000000"})

def test_cancelled_preview_cannot_execute_and_inputs_are_frozen():
    class Actions:
        calls=0
        def execute(self,*args):self.calls+=1;return {"status":"completed"}
    actions=Actions();machine=ConfirmationMachine(actions);inputs={"phone":"original"}
    preview=machine.preview("a","update_contact",inputs);inputs["phone"]="changed"
    assert preview.inputs["phone"]=="original"
    machine.confirm(preview.preview_id,False,"a")
    assert machine.confirm(preview.preview_id,True,"a").state=="CANCELLED"
    assert actions.calls==0
    with pytest.raises(KeyError):machine.confirm(preview.preview_id,True,"b")

def test_parallel_confirmations_execute_once():
    class Actions:
        calls=0
        def execute(self,*args):self.calls+=1;return {"status":"completed"}
    actions=Actions();machine=ConfirmationMachine(actions);preview=machine.preview("a","update_contact",{})
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _:machine.confirm(preview.preview_id,True,"a"),range(8)))
    assert actions.calls==1

def test_old_preview_invalidated_by_new_preview():
    machine=ConfirmationMachine(None)
    old=machine.preview("a","first",{})
    new=machine.preview("a","second",{})
    assert old.state=="CANCELLED" and new.state=="WAITING_CONFIRMATION"

def test_context_restores_scenario_slots_without_leaking_between_topics():
    conversation=Conversation()
    def result(sid,slots):return {"selected":[{"id":sid}],"language":"ru","extracted_slots":slots}
    conversation.update(result("SC27",{"policy_number":"first"}))
    conversation.update(result("SC29",{"contact_field":"email"}))
    assert "policy_number" not in conversation.context()["slots"]
    conversation.update(result("SC27",{}))
    assert conversation.context()["slots"]=={"policy_number":"first"}
    context=conversation.context();context["slots"].clear()
    assert conversation.state["slots"]

def test_numeric_alternative_confidence_triggers_clarification():
    result=apply({"selected":[{"id":"SC01","confidence":.9}],"alternatives":[{"id":"SC02","confidence":.8}],"clarification":{}})
    assert result["selected"][0]["id"]=="SYS_UNCLEAR"
    assert {item["id"] for item in result["alternatives"]}=={"SC01","SC02"}
    assert "SC01" not in result["clarification"]["question"]

def test_repeated_system_uncertainty_escalates():
    result=apply({"selected":[{"id":"SYS_UNCLEAR","confidence":"low"}],"alternatives":[]},1)
    assert result["handoff"]["queue"]=="operator_general"

@pytest.mark.parametrize("failure", [HTTPError("https://example.invalid",401,"unauthorized",{},None), URLError("private network details"), TimeoutError("private details")])
def test_provider_errors_are_safe(monkeypatch,failure):
    def fail(*args,**kwargs):raise failure
    monkeypatch.setattr("app.routing.provider_client.urlopen",fail)
    with pytest.raises(RuntimeError, match="LLM provider") as error:OpenAICompatibleClient("https://example.invalid","test-secret","test").route("JSON")
    assert "private" not in str(error.value) and "test-secret" not in str(error.value)

@pytest.mark.parametrize("response", [{}, {"choices":[]}, {"choices":[{"message":{"content":None}}]}, {"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}, {"choices":[{"message":{"content":"[]"}}]}])
def test_provider_response_shape_is_checked(monkeypatch,response):
    monkeypatch.setattr("app.routing.provider_client.urlopen",lambda *args,**kwargs:BytesIO(json.dumps(response).encode()))
    with pytest.raises(RuntimeError,match="invalid response"):OpenAICompatibleClient("https://example.invalid","test","test").route("JSON")

def test_mock_action_accepts_alternative_inputs(snapshot):
    assert MockActions(snapshot).execute("find_client",{"phone":"+77010000001"},"test")["status"]=="completed"

def test_nested_trace_fields_are_masked():
    raw={"slots":{"iin":"850314300121","drivers_iin":["850314300121"],"new_value":"private"},"selected":[{"reason":"Phone +77010000001"}]}
    masked=redact(raw)
    assert "850314300121" not in json.dumps(masked)
    assert "+77010000001" not in json.dumps(masked)
    assert raw["slots"]["iin"]=="850314300121"
