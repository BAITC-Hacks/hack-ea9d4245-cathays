from dataclasses import dataclass,field
from uuid import uuid4
from copy import deepcopy
from threading import RLock
@dataclass
class Conversation:
 id:str=field(default_factory=lambda:str(uuid4()));turns:list=field(default_factory=list);cache:dict=field(default_factory=dict);state:dict=field(default_factory=lambda:{"active_scenario":None,"suspended":[],"slots":{},"language_history":[],"clarification_attempts":0})
 lock:object=field(default_factory=RLock,repr=False)
 def context(self):return deepcopy(self.state)
 def update(self,result):
  sid=result["selected"][0]["id"]
  previous=self.state["active_scenario"]
  if sid.startswith("SC") and previous and sid!=previous:
   self.state.setdefault("scenario_slots",{})[previous]=deepcopy(self.state["slots"])
   if previous not in self.state["suspended"]:self.state["suspended"].append(previous)
   self.state["slots"]=deepcopy(self.state.get("scenario_slots",{}).get(sid,{}));result["topic_changed"]=True
   if sid in self.state["suspended"]:self.state["suspended"].remove(sid)
  if sid.startswith("SC"):
   self.state["active_scenario"]=sid
   self.state["slots"].update(result["extracted_slots"])
  self.state["language_history"].append(result["language"]);self.state["clarification_attempts"]=(self.state["clarification_attempts"]+1 if sid=="SYS_UNCLEAR" else 0)
class ConversationStore:
 def __init__(self):self.data={}
 def create(self):c=Conversation();self.data[c.id]=c;return c
 def get(self,id):
  if id not in self.data:raise KeyError(id)
  return self.data[id]
