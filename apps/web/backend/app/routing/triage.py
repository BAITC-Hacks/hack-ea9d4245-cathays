import re
def language(text: str) -> str:
    kk=set("әіңғүұқөһәі")
    return "mixed" if any(c in kk for c in text.lower()) and re.search(r"[ыэъё]",text.lower()) else ("kk" if any(c in kk for c in text.lower()) else "ru")
def triage(text: str) -> dict:
    return {"language":language(text),"segments":[text],"phones":re.findall(r"\+?\d[\d\s-]{7,}\d",text),"urgent":bool(re.search(r"авари|жол апат|мошенн|алаяқ",text,re.I))}
