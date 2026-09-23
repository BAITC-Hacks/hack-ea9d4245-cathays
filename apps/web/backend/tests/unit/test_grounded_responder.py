from app.dataset.repository import load_snapshot
from app.grounding.responder import respond
from app.settings import settings

def test_business_response_is_catalog_grounded():
    snapshot=load_snapshot(settings.dataset_path)
    result={"selected":[{"id":"SC01"}],"language":"ru","clarification":{"required":False}}
    assert respond(snapshot,result,{"mode":"information"})==snapshot.scenarios["SC01"]["responses"]["ru"]["opening"]
