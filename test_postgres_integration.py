import os,unittest
from cloud_storage import PostgresStorage
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"isolated PostgreSQL required")
class PostgresTests(unittest.TestCase):
    def test_restart_and_dedup(self):
        dsn=os.environ["NEXUS_TEST_DSN"]
        draft={"url":"https://example.org/integration","text":"Тест","preview":{"mode":"dry-run","sent":False},"publication_eligible":False}
        s=PostgresStorage(dsn)
        s.db.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1) ON CONFLICT(singleton) DO UPDATE SET starts_at=EXCLUDED.starts_at,runs=1")
        self.assertTrue(s.save(draft)); s.close()
        s=PostgresStorage(dsn)
        self.assertFalse(s.save(draft)); self.assertIn(draft,s.pending()); s.close()

    def test_atomic_budget(self):
        from concurrent.futures import ThreadPoolExecutor
        dsn=os.environ["NEXUS_TEST_DSN"]
        def attempt(_):
            s=PostgresStorage(dsn)
            try: return s.reserve_run()
            finally: s.close()
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(attempt,range(8))),1)
        self.assertFalse(attempt(0))
