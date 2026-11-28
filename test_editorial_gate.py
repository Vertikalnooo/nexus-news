import unittest
from editorial_gate import eligible_for_review, publication_eligible
class GateTests(unittest.TestCase):
    def test_numbers(self):
        self.assertFalse(eligible_for_review("Inflation 3%", "Инфляция 4%"))
        self.assertTrue(eligible_for_review("Inflation 3%", "Инфляция 3%"))
    def test_never_authorize(self):
        for draft in ({}, {"publication_eligible":True}, {"review_required":False}):
            self.assertFalse(publication_eligible(draft))
