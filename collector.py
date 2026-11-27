"""Read-only collection and deterministic ranking; no Telegram."""
import json, re, logging
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler
from engine import parse_rss

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def fetch(url):
    if not url.startswith('https://'): raise ValueError('HTTPS required')
    with build_opener(NoRedirect()).open(Request(url, headers={'User-Agent':'NEXUS-News/1.0'}), timeout=12) as response:
        data=response.read(2_000_001)
        if len(data)>2_000_000: raise ValueError('feed too large')
        return data

def score(item):
    title=item['title'].casefold()
    rules=[(35,r'\b(rate cut|rate hike|interest rates|ceasefire|earthquake|sanctions)\b'),(25,r'\b(bitcoin|ethereum|inflation|central bank|artificial intelligence|openai|bankruptcy)\b'),(15,r'\b(launch|regulation|acquisition|election|earnings)\b')]
    return min(100, 20+sum(weight for weight, pattern in rules if re.search(pattern,title)))

def collect(sources, loader=fetch, now=None):
    now=now or datetime.now(timezone.utc)
    items=[]
    failures=[]
    for source in sources:
        try:
            for item in parse_rss(loader(source['url']),source['name'],now):
                item['category']=source['category']
                item['score']=score(item)
                items.append(item)
        except Exception as exc:
            failures.append(source['name'])
            logging.warning('Feed failed: %s (%s)',source['name'],type(exc).__name__)
    return sorted(items,key=lambda i:(i['score'],i['date']),reverse=True),failures

if __name__=='__main__':
    sources=json.loads(Path(__file__).with_name('sources.json').read_text())
    items, failures=collect(sources)
    print(json.dumps({'items':items[:20],'failed_sources':failures},ensure_ascii=False,indent=2))
    if len(failures)==len(sources): raise SystemExit(1)
