from huggingface_hub import snapshot_download
import os
if any(os.getenv(k) for k in ("NEXUS_DATABASE_URL","TELEGRAM_BOT_TOKEN","GEMINI_API_KEY")):
    raise SystemExit("Refusing model preparation with runtime credentials")
snapshot_download("Helsinki-NLP/opus-mt-en-ru",revision="bb09c99d180016eac6819df3dae68edb1690fdee",local_dir="model",allow_patterns=["*.json","*.spm","*.safetensors","pytorch_model.bin"])
