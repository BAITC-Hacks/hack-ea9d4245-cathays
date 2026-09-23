import json
from urllib.request import Request, urlopen
class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str): self.base_url,self.api_key,self.model=base_url.rstrip("/"),api_key,model
    def route(self, prompt: str) -> dict:
        if not (self.base_url and self.api_key and self.model): raise RuntimeError("LLM provider is not configured")
        payload={"model":self.model,"messages":[{"role":"user","content":prompt}],"response_format":{"type":"json_object"},"temperature":0}
        request=Request(f"{self.base_url}/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"})
        with urlopen(request,timeout=30) as response: data=json.load(response)
        return json.loads(data["choices"][0]["message"]["content"])
