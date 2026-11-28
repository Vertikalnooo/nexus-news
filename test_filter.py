import unittest
from collector import collect, score
from test_engine import rss, NOW
class FilterTests(unittest.TestCase):
    def test_duplicate_feeds(self):
        sources=[dict(name=n,url='https://example.org',category='world') for n in ['A','B']]
        items, failures=collect(sources,lambda url:rss(),NOW)
        self.assertEqual(len(items),1)
        self.assertEqual(failures,[])
    def test_promotion(self):
        self.assertLess(score({'title':'Sponsored bitcoin price prediction'}),score({'title':'Bitcoin'}))
