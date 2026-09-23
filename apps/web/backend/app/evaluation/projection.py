def prediction_map(results: dict[str, dict]) -> dict[str, list[str]]:
    """Project rich product routing results to the unmodified evaluator contract."""
    return {utterance_id:[item["id"] for item in result["selected"]] for utterance_id,result in results.items()}
