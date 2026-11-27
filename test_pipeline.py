import unittest,json,tempfile
from pathlib import Path
from pipeline import run
from storage import Storage
from test_engine import rss,NOW
class PipelineTests(unittest.TestCase):
    def test_preview_and_restart(self):
        sources=[dict(name="A",url="https://example.org",category="world")]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"queue.db"
            s=Storage(p)
            a=run(sources,s,lambda u:rss(),lambda t:"Новость",now=NOW,threshold=0)
            self.assertEqual(a["saved"],1)
            self.assertFalse(a["publication_enabled"])
            s.close()
            s=Storage(p)
            self.assertEqual(run(sources,s,lambda u:rss(),lambda t:"Новость",now=NOW,threshold=0)["saved"],0)
            s.close()
    def test_no_editor_no_draft(self):
        s=Storage(":memory:")
        self.assertEqual(run([dict(name="A",url="https://example.org",category="world")],s,lambda u:rss(),now=NOW,threshold=0)["saved"],0)
        s.close()
