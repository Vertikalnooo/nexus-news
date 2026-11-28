import unittest
from datetime import datetime,timezone
from macro_match import candidate
class MatchTests(unittest.TestCase):
    def test_candidate_not_actual(self):
        now=datetime(2026,11,28,tzinfo=timezone.utc)
        event=dict(id="x",currency="USD",impact="high",title="Unemployment Rate",date="2026-11-27T12:00:00+00:00")
        rows=[dict(series="LNS14000000",period="2026-10",value="4.1")]
        c=candidate(event,rows,"2026-10",now)
        self.assertEqual(c["candidate_value"],"4.1")
        self.assertFalse(c["release_verified"])
        self.assertIsNone(candidate(dict(event,impact="medium"),rows,"2026-10",now))
        self.assertIsNone(candidate(dict(event,currency="EUR"),rows,"2026-10",now))
        self.assertIsNone(candidate(dict(event,date="2026-12-01T12:00:00+00:00"),rows,"2026-10",now))
