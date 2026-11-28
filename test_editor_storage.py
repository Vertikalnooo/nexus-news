import unittest,tempfile
from pathlib import Path
from editor import edit, gemini_request, opus_translate
from storage import Storage
ITEM={"title":"Central bank holds rates","source":"Example","url":"https://example.org/a"}
class EditorTests(unittest.TestCase):
    def test_primary(self):
        d=edit(ITEM,lambda t:"ЦБ сохранил ставку",None)
        self.assertTrue(d["review_required"])
        self.assertEqual(d["url"],ITEM["url"])
    def test_fallback(self):
        self.assertEqual(edit(ITEM,lambda t:"English",lambda t:"ЦБ сохранил ставку")["provider"],"opus")
    def test_fail_closed(self):
        self.assertIsNone(edit(ITEM,None,None))
    def test_request(self):
        self.assertIn(ITEM["title"],gemini_request(ITEM)["contents"][0]["parts"][0]["text"])
    def test_opus_adapter(self):
        self.assertEqual(opus_translate("test",lambda *a,**k:[{"translation_text":"тест"}]),"тест")
    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"drafts.db"
            d=edit(ITEM,lambda t:"ЦБ сохранил ставку",None)
            s=Storage(p); self.assertTrue(s.save(d)); s.close()
            s=Storage(p); self.assertFalse(s.save(d)); self.assertEqual(s.pending(),[d]); s.close()
