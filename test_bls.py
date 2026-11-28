import unittest,json
from bls import parse_observations
class BLSTests(unittest.TestCase):
    def test_observations(self):
        raw={"status":"REQUEST_SUCCEEDED","Results":{"series":[{"seriesID":"CUSR0000SA0","data":[{"year":"2026","period":"M10","value":"320.2"},{"year":"2026","period":"M13","value":"320.2"}]}]}}
        rows=parse_observations(json.dumps(raw).encode())
        self.assertEqual(len(rows),1)
        self.assertFalse(rows[0]["release_verified"])
    def test_error(self):
        with self.assertRaises(ValueError): parse_observations(b'{"status":"REQUEST_FAILED"}')
