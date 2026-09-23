def mismatches(utterances, predictions, routing_results=None):
    routing_results=routing_results or {}
    return [{"id":u["id"],"input":u["text"],"expected":u["expected"],"predicted":predictions.get(u["id"],[]),"language":u["lang"],"type":u["type"],"alternatives":routing_results.get(u["id"],{}).get("alternatives",[])} for u in utterances if set(predictions.get(u["id"],[]))!=set(u["expected"])]
