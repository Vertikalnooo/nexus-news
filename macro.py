"""High-impact calendar preview. No publishing or automatic network polling."""
import json, hashlib, re
from datetime import datetime, timezone, timedelta
from collector import fetch
URL="https://nfs.faireconomy.media/ff_calendar_thisweek.json"
def parse_calendar(data):
    if len(data)>2_000_000: raise ValueError("oversize")
    rows=json.loads(data)
    if not isinstance(rows,list): raise ValueError("expected list")
    out={}
    for row in rows:
        if not isinstance(row,dict) or row.get("impact")!="High": continue
        try:
            title=row["title"].strip()
            currency=row["country"]
            if not title or len(title)>300 or not re.fullmatch(r"[A-Z]{3}",currency): continue
            dt=datetime.fromisoformat(row["date"])
            if dt.tzinfo is None: continue
            stamp=dt.astimezone(timezone.utc).isoformat()
            key=hashlib.sha256(json.dumps([currency,title,stamp]).encode()).hexdigest()
            values={k:row.get(k) if isinstance(row.get(k),str) and row[k].strip() else None for k in ("actual","forecast","previous")}
            out[key]=dict(id=key,title=title,currency=currency,date=stamp,impact="high",source="Forex Factory",url="https://www.forexfactory.com/calendar",**values)
        except (KeyError,ValueError,TypeError,AttributeError): continue
    return sorted(out.values(),key=lambda x:x["date"])
def previews(events,now):
    if now.tzinfo is None: raise ValueError("timezone required")
    for event in events:
        delta=datetime.fromisoformat(event["date"])-now
        if timedelta(0)<delta<=timedelta(minutes=15):
            yield dict(event,kind="upcoming",review_required=True)
        elif -timedelta(hours=2)<=delta<=timedelta(0) and event["actual"] is not None:
            yield dict(event,kind="release",review_required=True)
if __name__=="__main__":
    events=parse_calendar(fetch(URL))
    print(json.dumps({"high_impact_count":len(events),"actual_count":sum(e["actual"] is not None for e in events)}))
