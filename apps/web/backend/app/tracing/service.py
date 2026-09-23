from uuid import uuid4
from .redaction import redact_text, redact
def trace(conversation_id, turn_id, text, result, execution):
    return {"trace_id":str(uuid4()),"conversation_id":conversation_id,"turn_id":turn_id,"transcript":redact_text(text),"language":result["language"],"selected":redact(result["selected"]),"alternatives":redact(result["alternatives"]),"slots":redact(result["extracted_slots"]),"continuation":result["continuation"],"topic_changed":result["topic_changed"],"clarification":redact(result["clarification"]),"fallback":redact(result.get("fallback")),"handoff":redact(result.get("handoff")),"execution":redact(execution),"metadata":result["metadata"],"latency_ms":result["latency_ms"]}
