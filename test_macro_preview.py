import json,unittest
from datetime import datetime,timezone,timedelta
from pipeline import run
from storage import Storage
class MacroPreviewTests(unittest.TestCase):
    def test_preview(self):
        now=datetime(2026,11,28,12,tzinfo=timezone.utc)
        rows=[dict(title="<b>CPI</b>",country="USD",impact="High",date=(now+timedelta(minutes=10)).isoformat()),dict(title="Ignored",country="USD",impact="Medium",date=now.isoformat())]
        s=Storage(":memory:")
        try:
            result=run([],s,None,calendar_data=json.dumps(rows).encode(),now=now)
            self.assertEqual(result["saved"],1)
            p=s.pending()[0]["preview"]
            self.assertFalse(p["sent"])
            self.assertIn("&lt;b&gt;CPI&lt;/b&gt;",p["text"])
            self.assertEqual(run([],s,None,calendar_data=json.dumps(rows).encode(),now=now)["saved"],0)
        finally: s.close()
