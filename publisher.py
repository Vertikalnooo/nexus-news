"""Pure Telegram preview renderer. No token, transport, or send capability."""
from html import escape
from engine import canonical
def dry_run(draft):
    if draft.get("review_required") is not True: raise ValueError("review flag required")
    text=draft["text"].strip()
    source=draft["source"].strip()
    url=canonical(draft.get("source_url",draft["url"]))
    if not text or not source: raise ValueError("empty draft")
    body=f"<b>NEXUS</b>\n\n{escape(text)}\n\n<a href=\"{escape(url,quote=True)}\">{escape(source)}</a>"
    if len(body.encode("utf-16-le"))//2>4096: raise ValueError("oversize")
    return {"mode":"dry-run","sent":False,"parse_mode":"HTML","text":body}
