from uuid import uuid4
from .redaction import redact_text
def trace(conversation_id, turn_id, text, result, execution):
    return {"trace_id":str(uuid4()),"conversation_id":conversation_id,"turn_id":turn_id,"transcript":redact_text(text),"language":result["language"],"selected":result["selected"],"alternatives":result["alternatives"],"slots":result["extracted_slots"],"continuation":result["continuation"],"topic_changed":result["topic_changed"],"clarification":result["clarification"],"fallback":result.get("fallback"),"handoff":result.get("handoff"),"execution":execution,"metadata":result["metadata"],"latency_ms":result["latency_ms"]}
