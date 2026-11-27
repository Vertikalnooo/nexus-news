import os,unittest
from cloud_storage import PostgresStorage
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"isolated PostgreSQL required")
class PostgresTests(unittest.TestCase):
    def test_restart_and_dedup(self):
        dsn=os.environ["NEXUS_TEST_DSN"]
        draft={"url":"https://example.org/integration","text":"Тест"}
        s=PostgresStorage(dsn)
        self.assertTrue(s.save(draft)); s.close()
        s=PostgresStorage(dsn)
        self.assertFalse(s.save(draft)); self.assertIn(draft,s.pending()); s.close()
