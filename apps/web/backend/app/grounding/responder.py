def respond(snapshot, result, execution):
    selected=result["selected"][0]["id"]
    language="kk" if result.get("language")=="kk" else "ru"
    mode=execution["mode"]
    if mode=="cancel": return "Әрекет тоқтатылды. Ешқандай өзгеріс жасалмады." if language=="kk" else "Действие отменено. Изменения не внесены."
    if mode=="execute": return "Сынақ әрекеті орындалды. Бұл нақты сақтандыру операциясы емес." if language=="kk" else "Тестовое действие выполнено. Это не реальная страховая операция."
    if mode=="handoff": return "Сұрағыңызды маманға беру қажет. Бұл сынақ режимінде операторға нақты қосылу орындалмайды." if language=="kk" else "Ваш запрос нужно передать специалисту. В тестовом режиме фактическое соединение с оператором не выполняется."
    if mode=="collect_slot":
        prompt=snapshot.slots[execution["slot"]]["prompt"][language]
        if execution.get("error"): prompt=("Деректер бойынша клиент табылмады. " if language=="kk" else "Не удалось однозначно определить клиента по указанным данным. ")+prompt
        return prompt
    if mode=="preview":
        name=snapshot.scenarios[selected]["name"]
        return f"«{name}» сынақ әрекетін растайсыз ба? Әзірге ештеңе орындалмады." if language=="kk" else f"Подтвердите тестовое действие «{name}». Пока ничего не выполнено."
    if mode=="fallback": return "Әрекетті орындау мүмкін болмады. Маманның көмегі қажет." if language=="kk" else "Не удалось подготовить действие. Нужна помощь специалиста."
    if selected.startswith("SYS_"):
        if selected=="SYS_GOODBYE":return "Сау болыңыз!" if language=="kk" else "До свидания!"
        return result["clarification"].get("question") or ("Saqta сақтандыру қызметтері бойынша көмектесе аламын." if language=="kk" else "Я могу помочь с услугами страхования Saqta.")
    scenario=snapshot.scenarios[selected]
    language="kk" if result.get("language")=="kk" else "ru"
    response=scenario.get("responses",{}).get(language) or scenario.get("responses",{}).get("ru",{})
    return response.get("opening") or scenario["description"]
