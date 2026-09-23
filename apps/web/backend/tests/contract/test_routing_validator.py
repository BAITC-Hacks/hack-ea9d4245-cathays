import pytest
from app.dataset.repository import load_snapshot
from app.dataset.validator import validate
from app.routing.validator import validate as validate_result, RoutingValidationError
from app.settings import settings

@pytest.fixture
def snapshot():
    result = load_snapshot(settings.dataset_path)
    validate(result)
    return result

def test_rejects_unknown_selected_id(snapshot):
    with pytest.raises(RoutingValidationError):
        validate_result({"selected": [{"id": "NOPE"}]}, snapshot)

def test_accepts_system_intent(snapshot):
    result = validate_result({"selected": [{"id": "SYS_UNCLEAR", "confidence": "low", "reason": "x"}], "alternatives": [{"id": "SC01"}], "slots": {}}, snapshot)
    assert result["selected"][0]["id"] == "SYS_UNCLEAR"
