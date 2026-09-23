"""Evaluation requires a configured LLM provider; it never reads expected labels for routing."""
import json, subprocess, sys
from pathlib import Path
from app.main import conversations, router
root=Path(__file__).resolve().parents[1]; out=root/"artifacts"/"predictions.json"; out.parent.mkdir(exist_ok=True)
preds={}
for utterance in router.snapshot.utterances:
    result=router.route(utterance["text"],{})
    preds[utterance["id"]]=[x["id"] for x in result["selected"]]
out.write_text(json.dumps(preds,ensure_ascii=False),encoding="utf-8")
subprocess.run([sys.executable,str(router.snapshot.root/"evaluate.py"),str(out),str(router.snapshot.root/"dev_utterances.json")],check=False)
