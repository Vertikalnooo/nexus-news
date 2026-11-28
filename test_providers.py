import unittest,json
from unittest.mock import patch,MagicMock
from providers import Gemini
class ProviderTests(unittest.TestCase):
    def test_opt_in(self):
        with self.assertRaises(ValueError): Gemini("fake","gemini-test")
    def test_model_validation(self):
        with self.assertRaises(ValueError): Gemini("fake","../bad",free_tier_confirmed=True)
    @patch("providers.build_opener")
    def test_response(self,opener):
        response=opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value=json.dumps({"candidates":[{"finishReason":"STOP","content":{"parts":[{"text":json.dumps({"text":"Новость"})}]}}]}).encode()
        self.assertEqual(Gemini("fake","gemini-test",free_tier_confirmed=True,reserve=lambda:True)("News"),"Новость")
    @patch("providers.build_opener")
    def test_incomplete(self,opener):
        opener.return_value.open.return_value.__enter__.return_value.read.return_value=b'{"candidates":[{"finishReason":"MAX_TOKENS"}]}'
        with self.assertRaises(ValueError): Gemini("fake","gemini-test",free_tier_confirmed=True,reserve=lambda:True)("News")
    @patch("providers.build_opener")
    def test_quota_denied(self,opener):
        with self.assertRaises(ValueError): Gemini("fake","gemini-test",free_tier_confirmed=True,reserve=lambda:False)("News")
        opener.assert_not_called()
