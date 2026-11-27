"""Explicitly enabled translation adapters. No paid fallback or automatic retries."""
import json,re
from urllib.request import Request,build_opener
from collector import NoRedirect
from editor import gemini_request
class Gemini:
    def __init__(self,key,model,*,free_tier_confirmed=False):
        if not free_tier_confirmed or not key: raise ValueError("free tier must be confirmed")
        if not re.fullmatch(r"gemini-[a-zA-Z0-9.-]+",model): raise ValueError("invalid model")
        self.key,self.model=key,model
    def __call__(self,title):
        req=Request("https://generativelanguage.googleapis.com/v1beta/models/"+self.model+":generateContent",data=json.dumps(gemini_request({"title":title})).encode(),headers={"Content-Type":"application/json","x-goog-api-key":self.key},method="POST")
        with build_opener(NoRedirect()).open(req,timeout=20) as response:
            raw=response.read(1_000_001)
        if len(raw)>1_000_000: raise ValueError("oversize")
        obj=json.loads(raw)
        candidate=obj["candidates"][0]
        if candidate.get("finishReason")!="STOP": raise ValueError("incomplete")
        result=json.loads(candidate["content"]["parts"][0]["text"])
        return result["text"]
class Opus:
    def __init__(self,local_model):
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        self.tokenizer=AutoTokenizer.from_pretrained(local_model,local_files_only=True,trust_remote_code=False)
        self.model=AutoModelForSeq2SeqLM.from_pretrained(local_model,local_files_only=True,trust_remote_code=False)
        self.model.eval()
    def __call__(self,title):
        inputs=self.tokenizer(title,return_tensors="pt",truncation=True,max_length=256)
        result=self.model.generate(**inputs,max_new_tokens=256)
        return self.tokenizer.decode(result[0],skip_special_tokens=True)
