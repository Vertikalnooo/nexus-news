"""Manual preview runner; no Telegram, no paid API, no default cloud access."""
import os,json
from pathlib import Path
from collector import fetch
from pipeline import run
from cloud_storage import PostgresStorage
from providers import Opus
from gateway_adapter import GatewayAdapter
from gateway_client import request
from preview_window import allowed
from deadline import deadline, DeadlineExpired
from time import monotonic
from datetime import datetime,timezone
def main():
    if os.getenv("NEXUS_PREVIEW_ENABLED")!="true": raise SystemExit("preview disabled")
    if os.getenv("NEXUS_PREPARE_MODEL")=="true": raise SystemExit("runtime dependency installation disabled; use audited prebuilt environment")
    start=os.getenv("NEXUS_PREVIEW_START_UTC")
    if not allowed(start,datetime.now(timezone.utc)):
        print(json.dumps({"status":"window_closed"}))
        return
    dsn=os.environ["NEXUS_DATABASE_URL"]
    sources=json.loads(Path(__file__).with_name("sources.json").read_text())
    storage=PostgresStorage(dsn)
    try:
        if not storage.db.execute('SELECT nexus.reserve_preview_session()').fetchone()[0]:
            print(json.dumps({"status":"session_denied"}))
            return
        if not storage.reserve_run():
            print(json.dumps({"status":"budget_denied"}))
            return
        if not allowed(start,datetime.now(timezone.utc)): return
        before=monotonic()
        remaining=storage.db.execute("SELECT nexus.preview_remaining()").fetchone()[0]
        with deadline(min(540,remaining-(monotonic()-before))):
            model=Opus(os.environ["NEXUS_OPUS_MODEL"])
            adapter=GatewayAdapter(storage,request)
            print(json.dumps(run(sources,adapter,fetch,fallback=model,outbox=adapter,now=datetime.now(timezone.utc))))
    except DeadlineExpired:
        print(json.dumps({"status":"deadline_expired"}))
    finally: storage.close()
if __name__=="__main__": main()
