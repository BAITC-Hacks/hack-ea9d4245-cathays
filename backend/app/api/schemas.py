from typing import Any
from pydantic import BaseModel, Field

class Intent(BaseModel):
    id:str; confidence:float|str="medium"; reason:str=""
class Clarification(BaseModel):
    required:bool=False; question:str|None=None
class RoutingResult(BaseModel):
    selected:list[Intent]; alternatives:list[Intent]=Field(default_factory=list); language:str; extracted_slots:dict[str,Any]=Field(default_factory=dict); continuation:bool=False; topic_changed:bool=False; clarification:Clarification=Field(default_factory=Clarification)
class ApiError(BaseModel):
    code:str; message:str; trace_id:str|None=None
