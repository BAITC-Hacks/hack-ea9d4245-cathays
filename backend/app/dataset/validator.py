from .repository import DatasetSnapshot, SYSTEM_INTENTS

class DatasetContractError(ValueError): pass

def validate(snapshot: DatasetSnapshot) -> None:
    expected = {f"SC{i:02}" for i in range(1, 41)}
    if set(snapshot.scenarios) != expected: raise DatasetContractError("catalog must contain exactly SC01-SC40")
    for sid, scenario in snapshot.scenarios.items():
        for slot in scenario["slots"].get("required", []) + scenario["slots"].get("optional", []):
            if slot not in snapshot.slots: raise DatasetContractError(f"{sid} references unknown slot {slot}")
        for action in scenario.get("actions", []):
            if action not in snapshot.actions: raise DatasetContractError(f"{sid} references unknown action {action}")
        for boundary in scenario.get("not_this_if", []):
            if boundary["use_instead"] not in snapshot.scenarios and boundary["use_instead"] not in SYSTEM_INTENTS: raise DatasetContractError(f"{sid} invalid boundary")
        handoff = scenario.get("handoff")
        if handoff and handoff["queue"] not in snapshot.queues: raise DatasetContractError(f"{sid} invalid queue")
    if len(snapshot.slots) != 43 or len(snapshot.actions) != 31 or len(snapshot.queues) != 6: raise DatasetContractError("dataset cardinality mismatch")
