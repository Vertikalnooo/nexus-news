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
    sources=json.loads(Path(__file__).with_name("sources.json").read_text())
    storage=PostgresStorage(dsn)
    try:
        if not storage.reserve_run():
            print(json.dumps({"status":"budget_denied"}))
            return
        if os.getenv("NEXUS_PREPARE_MODEL")=="true":
            import subprocess,sys
            subprocess.run([sys.executable,"-m","pip","install","torch>=2.6,<3","--index-url","https://download.pytorch.org/whl/cpu"],check=True,timeout=240)
            subprocess.run([sys.executable,"-m","pip","install","transformers>=4.48,<5","sentencepiece","sacremoses"],check=True,timeout=120)
            from huggingface_hub import snapshot_download
            snapshot_download("Helsinki-NLP/opus-mt-en-ru",local_dir=os.environ["NEXUS_OPUS_MODEL"],allow_patterns=["*.json","*.spm","*.bin","*.safetensors"])
        model=Opus(os.environ["NEXUS_OPUS_MODEL"])
        print(json.dumps(run(sources,storage,fetch,fallback=model,now=datetime.now(timezone.utc))))
    finally: storage.close()
if __name__=="__main__": main()
