import json
from pathlib import Path
from collector import collect
from providers import Opus
from editor import edit
def main():
    items,failures=collect(json.loads(Path("sources.json").read_text()))
    model=Opus("model")
    sample=[]
    groups={}
    for item in items: groups.setdefault(item["category"],[]).append(item)
    while len(sample)<30 and any(groups.values()):
        for group in groups.values():
            if not group or len(sample)>=30: continue
            item=group.pop(0)
            draft=edit(item,None,model)
            sample.append(dict(title=item["title"],source=item["source"],url=item["url"],score=item["score"],category=item["category"],translation=draft["text"] if draft else None,review="pending"))
    print(json.dumps(dict(sample=sample,failed_sources=failures,publication_enabled=False),ensure_ascii=False))
    if len(sample)!=30: raise SystemExit("insufficient sample")
if __name__=="__main__": main()
