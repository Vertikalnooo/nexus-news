import unittest
from editorial_gate import eligible_for_review, publication_eligible, independent_review
class GateTests(unittest.TestCase):
    def test_numbers(self):
        self.assertFalse(eligible_for_review("Inflation 3%", "Инфляция 4%"))
        self.assertTrue(eligible_for_review("Inflation 3%", "Инфляция 3%"))
    def test_never_authorize(self):
        for draft in ({}, {"publication_eligible":True}, {"review_required":False}):
            self.assertFalse(publication_eligible(draft))
    def test_independent_review(self):
        self.assertEqual(independent_review("Inflation 3%","Инфляция 3%"),"unverified")
        self.assertEqual(independent_review("Inflation 3%","Инфляция 4%",lambda *_:True),"rejected")
        self.assertEqual(independent_review("Inflation 3%","Инфляция 3%",lambda *_:True),"candidate_verified")
        self.assertFalse(publication_eligible({"review":"candidate_verified"}))
