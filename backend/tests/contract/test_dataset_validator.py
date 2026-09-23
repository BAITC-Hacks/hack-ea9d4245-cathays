from app.dataset.repository import load_snapshot
from app.dataset.validator import validate
from app.settings import settings

def test_authoritative_contract_loads():
    snapshot = load_snapshot(settings.dataset_path)
    validate(snapshot)
    assert (len(snapshot.scenarios), len(snapshot.slots), len(snapshot.actions), len(snapshot.queues)) == (40, 43, 31, 6)
