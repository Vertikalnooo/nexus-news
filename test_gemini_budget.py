import os,unittest
from concurrent.futures import ThreadPoolExecutor
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class GeminiBudgetTests(unittest.TestCase):
    def test_concurrent_limit(self):
        import psycopg
        from gemini_budget import GeminiBudget
        def connect(): return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
        def reserve(_):
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                return GeminiBudget(db).reserve()
        with connect() as admin:
            admin.execute("DELETE FROM nexus.gemini_usage")
            admin.execute("DELETE FROM nexus.gemini_last")
            self.assertFalse(reserve(0))
            admin.execute("UPDATE nexus.gemini_policy SET daily_limit=3,minute_limit=1")
            try:
                with ThreadPoolExecutor(max_workers=8) as pool:
                    self.assertEqual(sum(pool.map(reserve,range(12))),1)
                for _ in range(2):
                    admin.execute("UPDATE nexus.gemini_last SET last_at=clock_timestamp()-interval '61 seconds'")
                    self.assertTrue(reserve(0))
                admin.execute("UPDATE nexus.gemini_last SET last_at=clock_timestamp()-interval '61 seconds'")
                self.assertFalse(reserve(0))
            finally:
                admin.execute("UPDATE nexus.gemini_policy SET daily_limit=0,minute_limit=0")
