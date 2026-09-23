from fastapi.testclient import TestClient
from app import main

def test_confirmation_turn_cancels_preview_without_execution():
    client=TestClient(main.app)
    conversation=client.post("/v1/conversations").json()["conversation_id"]
    preview=main.executor.machine.preview(conversation,"update_contact",{"phone":"+77000000000"})
    response=client.post(f"/v1/conversations/{conversation}/turns",json={"client_turn_id":"cancel-preview","preview_id":preview.preview_id,"confirmed":False})
    assert response.status_code==200
    assert response.json()["execution"]["status"]=="cancelled"
