def respond(snapshot, result, execution):
    selected=result["selected"][0]["id"]
    if selected.startswith("SYS_"):
        return result["clarification"].get("question") or "I can help with Saqta Insurance services."
    scenario=snapshot.scenarios[selected]
    language="kk" if result.get("language")=="kk" else "ru"
    response=scenario.get("responses",{}).get(language) or scenario.get("responses",{}).get("ru",{})
    if execution["mode"]=="preview": return response.get("closing") or "Please confirm the action."
    return response.get("opening") or scenario["description"]
