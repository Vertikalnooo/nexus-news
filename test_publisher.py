import unittest
from publisher import dry_run
class PublisherTests(unittest.TestCase):
    def test_escape(self):
        p=dry_run(dict(text="<b>Новость</b>",source="A&B",url="https://example.org",review_required=True))
        self.assertFalse(p["sent"])
        self.assertIn("&lt;b&gt;",p["text"])
        self.assertIn("A&amp;B",p["text"])
    def test_reject(self):
        for d in [dict(text="x",source="a",url="http://example.org",review_required=True),dict(text="x",source="a",url="https://example.org",review_required=False)]:
            with self.assertRaises(ValueError): dry_run(d)
