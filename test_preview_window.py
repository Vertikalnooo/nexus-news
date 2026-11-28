import unittest
from datetime import datetime,timedelta,timezone
from preview_window import allowed
class WindowTests(unittest.TestCase):
    def test_boundaries(self):
        start=datetime(2026,1,1,tzinfo=timezone.utc)
        for delta,expected in [(-1,False),(0,True),(1,True),(172799,True),(172800,False),(172801,False)]:
            self.assertEqual(allowed(start.isoformat(),start+timedelta(seconds=delta)),expected)
    def test_hourly(self):
        start=datetime(2026,1,1,tzinfo=timezone.utc)
        self.assertEqual(sum(allowed(start.isoformat(),start+timedelta(hours=h)) for h in range(72)),48)
    def test_invalid(self):
        now=datetime(2026,1,1,tzinfo=timezone.utc)
        for value in (None,"","bad","2026-01-01","2026-01-01T01:00:00+01:00"):
            self.assertFalse(allowed(value,now))
        self.assertFalse(allowed(now.isoformat(),now.replace(tzinfo=None)))
