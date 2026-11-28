import os,unittest
from concurrent.futures import ThreadPoolExecutor
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class SessionTests(unittest.TestCase):
    def test_session(self):
        import psycopg
        def connect(): return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
        def reserve(_):
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                return db.execute("SELECT nexus.reserve_preview_session()").fetchone()[0]
        with connect() as admin:
            admin.execute("DELETE FROM nexus.preview_session")
            self.assertFalse(reserve(0))
            admin.execute("INSERT INTO nexus.preview_session(singleton,starts_at) VALUES(true,clock_timestamp())")
            with ThreadPoolExecutor(max_workers=8) as pool:
                self.assertEqual(sum(pool.map(reserve,range(12))),1)
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                for sql in ("UPDATE nexus.preview_session SET starts_at=clock_timestamp()","DELETE FROM nexus.preview_session","INSERT INTO nexus.preview_session(singleton,starts_at) VALUES(true,clock_timestamp())"):
                    with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute(sql)
            admin.execute("UPDATE nexus.preview_session SET starts_at=clock_timestamp()-interval '48 hours'")
            self.assertFalse(reserve(0))
            admin.execute("UPDATE nexus.preview_session SET starts_at=clock_timestamp()-interval '1 hour',runs=48,last_run=NULL")
            self.assertFalse(reserve(0))
