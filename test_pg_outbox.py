import os,unittest,uuid
from concurrent.futures import ThreadPoolExecutor
from pg_outbox import PgOutbox,MockTelegram
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class PgOutboxTests(unittest.TestCase):
    def connect(self):
        import psycopg
        return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
    def test_concurrent_and_switch(self):
        with self.connect() as db:
            q=PgOutbox(db)
            key=q.enqueue(str(uuid.uuid4()),dict(mode="dry-run",sent=False))
            self.assertEqual(q.dispatch(key,MockTelegram(),approved=True),"disabled")
            db.execute("UPDATE nexus.publication_control SET enabled=true")
            try:
                def worker(i):
                    with self.connect() as conn: return PgOutbox(conn).dispatch(key,MockTelegram(),approved=True)
                with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(worker,range(8)))
                self.assertEqual(results.count("simulated"),1)
                self.assertEqual(results.count("blocked"),7)
                for outcome in ("timeout","429","403","500"):
                    k=q.enqueue(str(uuid.uuid4()),dict(mode="dry-run",sent=False))
                    self.assertEqual(q.dispatch(k,MockTelegram(outcome),approved=True),"unknown")
                    self.assertEqual(q.dispatch(k,MockTelegram(),approved=True),"blocked")
            finally: db.execute("UPDATE nexus.publication_control SET enabled=false")

    def test_worker_cannot_enable(self):
        import psycopg
        with self.connect() as db:
            db.execute("SET ROLE nexus_mock_worker")
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                db.execute("UPDATE nexus.publication_control SET enabled=true")
            with db.transaction():
                self.assertFalse(db.execute("SELECT nexus.lock_publication_switch()").fetchone()[0])
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                db.execute("DELETE FROM nexus.outbox")
    def test_switch_lock(self):
        import psycopg
        with self.connect() as a, self.connect() as b:
            with a.transaction():
                a.execute("SELECT nexus.lock_publication_switch()")
                b.execute("SET lock_timeout='200ms'")
                with self.assertRaises(psycopg.errors.LockNotAvailable):
                    b.execute("UPDATE nexus.publication_control SET enabled=false")
            b.execute("UPDATE nexus.publication_control SET enabled=false")
