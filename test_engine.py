import unittest, sqlite3
from datetime import datetime, timezone
from engine import canonical, parse_rss, preview
NOW=datetime(2026,11,28,12,tzinfo=timezone.utc)
def rss(date='Sat, 28 Nov 2026 11:00:00 GMT',link='https://example.org/a',title='Example news'):
    return f'<rss><channel><item><title>{title}</title><link>{link}</link><pubDate>{date}</pubDate></item></channel></rss>'.encode()
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(len(parse_rss(rss(),'Example',NOW)),1)
    def test_stale(self): self.assertEqual(parse_rss(rss('Fri, 27 Nov 2026 10:00:00 GMT'),'Example',NOW),[])
    def test_future(self): self.assertEqual(parse_rss(rss('Sat, 28 Nov 2026 13:00:00 GMT'),'Example',NOW),[])
    def test_bad_date(self): self.assertEqual(parse_rss(rss('bad'),'Example',NOW),[])
    def test_unsafe_url(self): self.assertEqual(parse_rss(rss(link='http://example.org'),'Example',NOW),[])
    def test_tracking(self): self.assertEqual(canonical('https://example.org/a?utm_source=x#b'),'https://example.org/a')
    def test_entity(self):
        with self.assertRaises(ValueError): parse_rss(b'<!DOCTYPE rss><rss/>','Example',NOW)
    def test_duplicate(self):
        db=sqlite3.connect(':memory:'); items=parse_rss(rss(),'Example',NOW)
        self.assertEqual(len(preview(items+items,db)),1); self.assertEqual(preview(items,db),[])
    def test_title_duplicate(self):
        db=sqlite3.connect(':memory:'); a=parse_rss(rss(),'Example',NOW); b=parse_rss(rss(link='https://example.org/b',title='EXAMPLE NEWS!'),'Other',NOW)
        self.assertEqual(len(preview(a+b,db)),1)
if __name__=='__main__': unittest.main()
