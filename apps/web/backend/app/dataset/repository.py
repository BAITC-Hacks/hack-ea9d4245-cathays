from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from pathlib import Path
SYSTEM_INTENTS={"SYS_OUT_OF_SCOPE","SYS_UNCLEAR","SYS_GOODBYE"}
@dataclass(frozen=True)
class DatasetSnapshot:
 root:Path; version:str; as_of_date:str; fingerprint:str; scenarios:dict; slots:dict; actions:dict; queues:set; knowledge:dict; backend:dict; dialogs:list; utterances:list
def _read(root,name):
 with (root/name).open(encoding="utf-8") as f:return json.load(f)
def load_snapshot(root:Path)->DatasetSnapshot:
 root=root.resolve(); s,sl,a=(_read(root,x) for x in ("scenarios.json","slots.json","actions.json")); raw=b"".join((root/x).read_bytes() for x in ("scenarios.json","slots.json","actions.json","knowledge_base.json","mock_backend.json"))
 return DatasetSnapshot(root,s["meta"]["version"],s["meta"]["as_of_date"],hashlib.sha256(raw).hexdigest()[:16],{x["scenario_id"]:x for x in s["scenarios"]},{x["name"]:x for x in sl["slots"]},{x["name"]:x for x in a["actions"]},set(a["queues"]),_read(root,"knowledge_base.json"),_read(root,"mock_backend.json"),_read(root,"dialogs_sample.json")["dialogs"],_read(root,"dev_utterances.json")["utterances"])
