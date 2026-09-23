from app.routing.decision_policy import apply

def test_low_confidence_requests_clarification():
    result = apply({"selected": [{"id": "SC01", "confidence": "low", "reason": ""}], "alternatives": [{"id": "SC02", "confidence": "medium", "reason": ""}], "clarification": {"required": False}})
    assert result["selected"][0]["id"] == "SYS_UNCLEAR"
    assert result["clarification"]["required"]
