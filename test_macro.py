import unittest,json
from datetime import datetime,timezone
from macro import parse_calendar,previews
NOW=datetime(2026,11,28,12,tzinfo=timezone.utc)
ROW=dict(title="CPI",country="USD",date="2026-11-28T13:10:00+01:00",impact="High",forecast="3%",previous="2%")
class MacroTests(unittest.TestCase):
    def test_only_high(self):
        self.assertEqual(len(parse_calendar(json.dumps([ROW,dict(ROW,impact="Medium"),dict(ROW,impact="Low"),ROW]).encode())),1)
    def test_utc_and_warning(self):
        e=parse_calendar(json.dumps([ROW]).encode())
        self.assertEqual(e[0]["date"],"2026-11-28T12:10:00+00:00")
        self.assertEqual(list(previews(e,NOW))[0]["kind"],"upcoming")
    def test_missing_actual(self):
        e=parse_calendar(json.dumps([dict(ROW,date="2026-11-28T11:50:00Z")]).encode())
        self.assertEqual(list(previews(e,NOW)),[])
    def test_release(self):
        e=parse_calendar(json.dumps([dict(ROW,date="2026-11-28T11:50:00Z",actual="3.2%")]).encode())
        self.assertEqual(list(previews(e,NOW))[0]["kind"],"release")
    def test_invalid(self):
        with self.assertRaises(ValueError): parse_calendar(b"<html>blocked</html>")
    def test_naive(self):
        self.assertEqual(parse_calendar(json.dumps([dict(ROW,date="2026-11-28T12:10:00")]).encode()),[])
