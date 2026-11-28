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

    def test_preview_and_cap(self):
        s=Storage(":memory:")
        try:
            sources=[dict(name="A",url="https://example.org",category="world")]
            result=run(sources,s,lambda u:rss(),lambda t:"<b>Новость</b>",now=NOW,threshold=0,max_translations=1)
            self.assertEqual(result["translation_attempts"],1)
            self.assertFalse(s.pending()[0]["preview"]["sent"])
            self.assertIn("&lt;b&gt;",s.pending()[0]["preview"]["text"])
            result=run(sources,s,lambda u:rss(),lambda t:self.fail("must not translate"),now=NOW,threshold=0,max_translations=0)
            self.assertEqual(result["translation_attempts"],0)
        finally: s.close()
