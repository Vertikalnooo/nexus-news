import unittest
from engine import parse_rss
from storage import Storage
from test_engine import NOW
class HardeningTests(unittest.TestCase):
    def test_utf16_dtd(self):
        with self.assertRaises(ValueError):
            parse_rss('<?xml version="1.0"?><!DOCTYPE rss><rss/>'.encode("utf-16"),"A",NOW)
    def test_title_unique(self):
        s=Storage(":memory:")
        try:
            self.assertTrue(s.save(dict(url="https://example.org/a",title_key="key")))
            self.assertTrue(s.contains("https://example.org/b","key"))
            self.assertFalse(s.save(dict(url="https://example.org/b",title_key="key")))
        finally: s.close()
