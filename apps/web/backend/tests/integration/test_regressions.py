from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from fastapi.testclient import TestClient
from app import main
import pytest

@pytest.fixture
def client():return TestClient(main.app,raise_server_exceptions=False)

def new_conversation(client):return client.post("/v1/conversations").json()["conversation_id"]

def route(sid="SC29",slots=None):
    return {"selected":[{"id":sid,"confidence":"high","reason":"test"}],"alternatives":[],"language":"ru","extracted_slots":slots or {},"continuation":False,"topic_changed":False,"clarification":{"required":False},"metadata":{},"latency_ms":{"total":{"duration_ms":12,"status":"measured"}}}

@pytest.mark.parametrize("body", [{}, {"client_turn_id":"x","text":"  "}, {"client_turn_id":" ","text":"Hi"}, {"client_turn_id":"x","text":"Hi","input_mode":"audio"}, {"client_turn_id":"x","preview_id":"p","confirmed":"yes"}, {"client_turn_id":"x","confirmed":True}])
def test_invalid_requests_return_json_422(client,body):
    response=client.post(f"/v1/conversations/{new_conversation(client)}/turns",json=body)
    assert response.status_code==422
    assert response.json()["code"]=="invalid_request"

def test_exception_handler_returns_safe_json(client,monkeypatch):
    def fail(*args):raise RuntimeError("secret internal detail")
    monkeypatch.setattr(main.router,"route",fail)
    response=client.post(f"/v1/conversations/{new_conversation(client)}/turns",json={"client_turn_id":"x","text":"Hi"})
    assert response.status_code==500 and response.json()["code"]=="internal_error"
    assert "secret" not in response.text

def test_cannot_confirm_another_conversations_preview(client):
    first,second=new_conversation(client),new_conversation(client)
    preview=main.executor.machine.preview(first,"renew_policy",{"policy_number":"SQ-OGPO-104501"})
    response=client.post(f"/v1/conversations/{second}/turns",json={"client_turn_id":"x","preview_id":preview.preview_id,"confirmed":True})
    assert response.status_code==404
    assert preview.state=="WAITING_CONFIRMATION"

def test_unknown_preview_is_404_instead_of_500(client):
    response=client.post(f"/v1/conversations/{new_conversation(client)}/turns",json={"client_turn_id":"x","preview_id":"unknown","confirmed":True})
    assert response.status_code==404 and response.json()["code"]=="preview_not_found"

def test_multi_turn_collection_uses_prior_slots_and_does_not_claim_early_success(client,monkeypatch):
    results=iter([route(slots={"contact_field":"email"}),route(slots={"new_value":"updated@example.test"}),route(slots={"phone":"+77010000001"})])
    monkeypatch.setattr(main.router,"route",lambda *args:next(results))
    cid=new_conversation(client)
    replies=[client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":str(i),"text":"test"}) for i in range(3)]
    assert all(response.status_code==200 for response in replies)
    assert replies[0].json()["execution"]["slot"]=="new_value"
    assert replies[1].json()["execution"]["slot"]=="phone"
    last=replies[2].json()
    assert last["execution"]["mode"]=="preview"
    assert "Пока ничего не выполнено" in last["assistant_message"]
    preview=main.executor.machine.records[last["execution"]["preview_id"]]
    assert preview.inputs["client_id"]=="C001" and preview.inputs["new_value"]=="updated@example.test"
    cancelled=client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":"cancel","preview_id":preview.preview_id,"confirmed":False})
    assert cancelled.status_code==200 and "Действие отменено" in cancelled.json()["assistant_message"]

def test_duplicate_concurrent_turns_route_once(client,monkeypatch):
    calls=[]
    def scripted(*args):calls.append(1);return route("SC31")
    monkeypatch.setattr(main.router,"route",scripted)
    cid=new_conversation(client)
    def send(_):return client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":"same","text":"test"}).json()
    with ThreadPoolExecutor(max_workers=3) as pool:replies=list(pool.map(send,range(3)))
    assert len(calls)==1 and all(reply==replies[0] for reply in replies)

def test_last_turn_preview_can_be_cancelled(client):
    cid=new_conversation(client)
    main.conversations.get(cid).turns.extend([{}]*10)
    preview=main.executor.machine.preview(cid,"renew_policy",{"policy_number":"SQ-OGPO-104501"})
    response=client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":"cancel","preview_id":preview.preview_id,"confirmed":False})
    assert response.status_code==200
    response=client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":"new","text":"Hello"})
    assert response.status_code==409 and response.json()["code"]=="conversation_limit"

def test_sensitive_slots_are_not_exposed_in_trace_or_history(client,monkeypatch):
    monkeypatch.setattr(main.router,"route",lambda *args:route("SC31",{"phone":"+77010000001"}))
    cid=new_conversation(client)
    response=client.post(f"/v1/conversations/{cid}/turns",json={"client_turn_id":"x","text":"+77010000001"})
    assert response.status_code==200
    for result in [response,client.get(f"/v1/conversations/{cid}"),client.get(f"/v1/conversations/{cid}/traces/1")]:
        assert "+77010000001" not in result.text

def test_local_frontend_origin_is_allowed(client):
    response=client.options("/v1/conversations",headers={"Origin":"http://localhost:5173","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"})
    assert response.status_code==200
    assert response.headers["access-control-allow-origin"]=="http://localhost:5173"
