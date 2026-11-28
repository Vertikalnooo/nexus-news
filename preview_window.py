"""Fixed UTC preview window; missing or malformed configuration denies runs."""
from datetime import datetime, timedelta, timezone
def allowed(start, now):
    if not isinstance(start,str) or not isinstance(now,datetime) or now.tzinfo is None:
        return False
    try:
        origin=datetime.fromisoformat(start.replace("Z","+00:00"))
        if origin.tzinfo is None or origin.utcoffset()!=timedelta(0): return False
        return origin <= now < origin+timedelta(hours=48)
    except (ValueError,OverflowError,TypeError):
        return False
