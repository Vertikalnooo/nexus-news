import unittest
from datetime import datetime, timezone
from collector import collect, score
from test_engine import rss, NOW
class CollectorTests(unittest.TestCase):
    def test_rank(self):
        self.assertGreater(score({'title':'Central bank announces rate cut'}),score({'title':'Local event'}))
    def test_bounded(self):
        self.assertLessEqual(score({'title':'rate cut bitcoin launch'}),100)
    def test_collect(self):
        sources=[{'name':'A','url':'https://example.org','category':'world'}]
        items, failures=collect(sources,lambda url:rss(),NOW)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['category'],'world')
        self.assertEqual(failures,[])
    def test_failure_isolated(self):
        sources=[{'name':'A','url':'https://a.example','category':'world'},{'name':'B','url':'https://b.example','category':'crypto'}]
        def loader(url):
            if 'a.example' in url: raise TimeoutError()
            return rss()
        items, failures=collect(sources,loader,NOW)
        self.assertEqual(len(items),1)
        self.assertEqual(failures,['A'])
