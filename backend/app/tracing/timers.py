from time import perf_counter
class Timers:
 def __init__(self):self._start=perf_counter();self.stages={}
 def measure(self,name):
  outer=self
  class Scope:
   def __enter__(self):self.started=perf_counter();return self
   def __exit__(self,*_):outer.stages[name]={"duration_ms":round((perf_counter()-self.started)*1000),"status":"measured"}
  return Scope()
 def fail(self,name):self.stages[name]={"duration_ms":None,"status":"failed"}
 def result(self):return {**self.stages,"total":{"duration_ms":round((perf_counter()-self._start)*1000),"status":"measured"}}
