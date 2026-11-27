"""Integrated preview pipeline; never publishes or invokes paid services itself."""
from collector import collect
from editor import edit
from macro import parse_calendar, previews
from datetime import datetime, timezone
def run(sources, storage, loader, primary=None, fallback=None, calendar_data=None, now=None, threshold=55):
    now=now or datetime.now(timezone.utc)
    items, failures=collect(sources,loader,now)
    saved=0
    for item in items:
        if item["score"]<threshold: continue
        draft=edit(item,primary,fallback)
        if draft is not None: saved+=storage.save(draft)
    if calendar_data is not None:
        for event in previews(parse_calendar(calendar_data),now):
            draft=dict(event, url=event["url"]+"#"+event["id"]+"-"+event["kind"], source_url=event["url"])
            saved+=storage.save(draft)
    return {"saved":saved,"failed_sources":failures,"publication_enabled":False}
