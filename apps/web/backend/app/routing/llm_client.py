from typing import Protocol
class LLMClient(Protocol):
    def route(self, prompt: str) -> dict: ...

class ScriptedLLM:
    """Test-only adapter: callers inject valid or invalid structured model output."""
    def __init__(self, output: dict): self.output=output
    def route(self, prompt: str) -> dict: return self.output
