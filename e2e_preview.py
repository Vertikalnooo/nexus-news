import json,tempfile
from pathlib import Path
from collector import fetch
from pipeline import run
from providers import Opus
from storage import Storage
def main():
    sources=json.loads(Path("sources.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        s=Storage(Path(tmp)/"preview.db")
        try:
            result=run(sources,s,fetch,fallback=Opus("model"),threshold=0,max_translations=3)
            drafts=s.pending()
            assert drafts and all(d["preview"]["sent"] is False for d in drafts)
            assert result["publication_enabled"] is False
            print(json.dumps(result))
        finally: s.close()
if __name__=="__main__": main()
