"""Manual preview runner; no Telegram, no paid API, no default cloud access."""
import os,json
from pathlib import Path
from collector import fetch
from pipeline import run
from cloud_storage import PostgresStorage
from providers import Opus
from pg_outbox import PgOutbox
from datetime import datetime,timezone
def main():
    if os.getenv("NEXUS_PREVIEW_ENABLED")!="true": raise SystemExit("preview disabled")
    if os.getenv("NEXUS_PREPARE_MODEL")=="true": raise SystemExit("runtime dependency installation disabled; use audited prebuilt environment")
    dsn=os.environ["NEXUS_DATABASE_URL"]
    sources=json.loads(Path(__file__).with_name("sources.json").read_text())
    storage=PostgresStorage(dsn)
    try:
        if not storage.reserve_run():
            print(json.dumps({"status":"budget_denied"}))
            return
        model=Opus(os.environ["NEXUS_OPUS_MODEL"])
        print(json.dumps(run(sources,storage,fetch,fallback=model,outbox=PgOutbox(storage.db),now=datetime.now(timezone.utc))))
    finally: storage.close()
if __name__=="__main__": main()
