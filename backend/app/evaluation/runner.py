import json, subprocess, sys
from pathlib import Path
from .projection import prediction_map
from .reporting import mismatches

def run(router, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True,exist_ok=True)
    results={utterance["id"]:router.route(utterance["text"],{}) for utterance in router.snapshot.utterances}
    predictions=prediction_map(results); path=output_dir/"predictions.json"
    path.write_text(json.dumps(predictions,ensure_ascii=False),encoding="utf-8")
    process=subprocess.run([sys.executable,str(router.snapshot.root/"evaluate.py"),str(path),str(router.snapshot.root/"dev_utterances.json")],capture_output=True,text=True)
    report={"predictions_path":str(path),"returncode":process.returncode,"stdout":process.stdout,"stderr":process.stderr,"catalog_version":router.snapshot.version,"errors":mismatches(router.snapshot.utterances,predictions,results)}
    (output_dir/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
