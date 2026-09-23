from app.evaluation.projection import prediction_map
def test_preserves_ordered_selected_ids_only():
    assert prediction_map({"U1":{"selected":[{"id":"SC27"},{"id":"SC04"}],"alternatives":[{"id":"SC01"}]}})=={"U1":["SC27","SC04"]}
