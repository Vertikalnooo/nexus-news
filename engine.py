"""Offline-first RSS preview; never publishes."""
import re, sqlite3, hashlib, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def canonical(url):
    p=urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password: raise ValueError('unsafe URL')
    return urlunsplit((p.scheme,p.netloc.lower(),p.path or '/',urlencode(sorted((k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_'))),''))

def parse_rss(data, source, now):
    if len(data)>2_000_000 or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper(): raise ValueError('unsafe XML')
    root=ET.fromstring(data)
    out=[]
    for item in root.findall('./channel/item'):
        try:
            title=' '.join((item.findtext('title') or '').split())
            url=canonical(item.findtext('link') or '')
            date=parsedate_to_datetime(item.findtext('pubDate') or '')
            if not title or date.tzinfo is None or not now-timedelta(hours=24)<=date<=now: continue
            out.append({'title':title[:300],'url':url,'source':source,'date':date.isoformat()})
        except (ValueError,TypeError,OverflowError): continue
    return out

def preview(items, db):
    db.execute('CREATE TABLE IF NOT EXISTS seen (url TEXT UNIQUE, title TEXT UNIQUE)')
    out=[]
    with db:
        for item in items:
            key=hashlib.sha256(re.sub(r'[^\w]+',' ',item['title'].casefold()).strip().encode()).hexdigest()
            cur=db.execute('INSERT OR IGNORE INTO seen VALUES (?,?)',(item['url'],key))
            if cur.rowcount: out.append(item)
    return out
