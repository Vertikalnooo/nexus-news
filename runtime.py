"""Manual preview runner; no Telegram, no paid API, no default cloud access."""
import os,json
from pathlib import Path
from collector import fetch
from pipeline import run
from cloud_storage import PostgresStorage
from providers import Opus
from datetime import datetime,timezone
def main():
    if os.getenv("NEXUS_PREVIEW_ENABLED")!="true": raise SystemExit("preview disabled")
    dsn=os.environ["NEXUS_DATABASE_URL"]
    model=Opus(os.environ["NEXUS_OPUS_MODEL"])
    sources=json.loads(Path(__file__).with_name("sources.json").read_text())
    storage=PostgresStorage(dsn)
    try:
        print(json.dumps(run(sources,storage,fetch,fallback=model,now=datetime.now(timezone.utc))))
    finally: storage.close()
if __name__=="__main__": main()
