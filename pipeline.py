"""Integrated preview pipeline; never publishes or invokes paid services itself."""
from collector import collect
from publisher import dry_run
from editor import edit
from macro import parse_calendar, previews
from datetime import datetime, timezone
def run(sources, storage, loader, primary=None, fallback=None, calendar_data=None, now=None, threshold=55, max_translations=10):
    now=now or datetime.now(timezone.utc)
    items, failures=collect(sources,loader,now)
    saved=0
    attempts=0
    rendered=0
    for item in items:
        if item["score"]<threshold: continue
        if attempts>=max_translations: break
        attempts+=1
        draft=edit(item,primary,fallback)
        if draft is not None:
            try: draft["preview"]=dry_run(draft)
            except (ValueError,TypeError,KeyError): continue
            rendered+=1
            saved+=storage.save(draft)
    if calendar_data is not None:
        for event in previews(parse_calendar(calendar_data),now):
            draft=dict(event, url=event["url"]+"#"+event["id"]+"-"+event["kind"], source_url=event["url"])
            saved+=storage.save(draft)
    return {"saved":saved,"rendered":rendered,"translation_attempts":attempts,"failed_sources":failures,"publication_enabled":False}
