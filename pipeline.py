"""Integrated preview pipeline; never publishes or invokes paid services itself."""
import hashlib,re,unicodedata
from collector import collect
from publisher import dry_run
from editor import edit
from editorial_gate import eligible_for_review, publication_eligible, independent_review
from macro import parse_calendar, previews
from datetime import datetime, timezone
def run(sources, storage, loader, primary=None, fallback=None, calendar_data=None, now=None, threshold=55, max_translations=10, outbox=None):
    now=now or datetime.now(timezone.utc)
    items, failures=collect(sources,loader,now)
    saved=0
    attempts=0
    rendered=0
    for item in items:
        if item["score"]<threshold: continue
        key=hashlib.sha256(re.sub(r"[^\w]+"," ",unicodedata.normalize("NFKC",item["title"]).casefold()).strip().encode()).hexdigest()
        if storage.contains(item["url"],key): continue
        if attempts>=max_translations: break
        attempts+=1
        draft=edit(item,primary,fallback)
        if draft is not None:
            try: draft["preview"]=dry_run(draft)
            except (ValueError,TypeError,KeyError): continue
            draft["editorial_checks_passed"]=eligible_for_review(item["title"],draft["text"])
            draft["editorial_review"]=independent_review(item["title"],draft["text"])
            draft["publication_eligible"]=publication_eligible(draft)
            draft["title_key"]=key
            rendered+=1
            saved+=storage.save(draft)
    if calendar_data is not None:
        for event in previews(parse_calendar(calendar_data),now):
            draft=dict(event, url=event["url"]+"#"+event["id"]+"-"+event["kind"], source_url=event["url"])
            draft["text"]="Экономический календарь: "+event["title"]+" ("+event["currency"]+")\nВремя UTC: "+event["date"]+"\n"+("Ожидается публикация." if event["kind"]=="upcoming" else "Значение календаря (не подтверждено независимо): "+str(event["actual"]))
            draft["preview"]=dry_run(draft)
            saved+=storage.save(draft)
    if outbox is not None:
        for draft in storage.pending():
            preview=draft.get("preview")
            if not isinstance(preview,dict) or preview.get("mode")!="dry-run" or preview.get("sent") is not False: continue
            # Existing outbox is mock-only; never confer publication authority.
            preview=dict(preview, publication_eligible=publication_eligible(draft), review_required=True)
            outbox.enqueue(draft.get("title_key") or draft["url"],preview)
    return {"saved":saved,"rendered":rendered,"translation_attempts":attempts,"failed_sources":failures,"publication_enabled":False}
