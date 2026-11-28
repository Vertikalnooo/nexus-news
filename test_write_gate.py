import os,unittest,uuid
from concurrent.futures import ThreadPoolExecutor
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class WriteGateTests(unittest.TestCase):
    def test_gate(self):
        import psycopg
        def connect(): return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
        key=str(uuid.uuid4())
        def attempt(_):
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                return db.execute("SELECT nexus.enqueue_preview(%s,%s::jsonb)",(key,'{"mode":"dry-run","sent":false}')).fetchone()[0]
        with connect() as admin:
            admin.execute("DELETE FROM nexus.preview_session")
            self.assertFalse(attempt(0))
            admin.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1)")
            with ThreadPoolExecutor(max_workers=8) as pool:
                self.assertEqual(sum(pool.map(attempt,range(8))),1)
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                    db.execute("INSERT INTO nexus.outbox(id,payload) VALUES('forbidden','{}')")
                self.assertFalse(db.execute("SELECT nexus.enqueue_preview('bad','{}')").fetchone()[0])
            admin.execute("UPDATE nexus.preview_session SET starts_at=clock_timestamp()-interval '49 hours'")
            self.assertFalse(attempt(0))
            with connect() as db:
                db.execute("SET ROLE nexus_preview")
                self.assertFalse(db.execute("SELECT nexus.save_preview('expired','{\"preview\":{\"mode\":\"dry-run\",\"sent\":false}}')").fetchone()[0])
