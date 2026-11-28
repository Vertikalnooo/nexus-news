import os,uuid,unittest
from concurrent.futures import ThreadPoolExecutor
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class JournalTests(unittest.TestCase):
    def test_reconcile_and_revoke(self):
        import psycopg
        from journal_gateway import JournalGateway
        def connect(): return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
        def gateway_connect():
            db=connect(); db.execute("SET ROLE nexus_write_gateway"); return db
        g=JournalGateway(gateway_connect)
        key=uuid.uuid4().hex; rid=uuid.uuid4(); payload={"mode":"dry-run","sent":False}
        with connect() as admin:
            admin.execute("DELETE FROM nexus.preview_session")
            admin.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1)")
            admin.execute("REVOKE EXECUTE ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) FROM nexus_preview")
            try:
                with connect() as db:
                    db.execute("SET ROLE nexus_preview")
                    with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute("SELECT nexus.enqueue_preview('forbidden','{}')")
                with ThreadPoolExecutor(max_workers=8) as pool:
                    self.assertTrue(all(pool.map(lambda _:g.request(rid,"enqueue",key,payload),range(8))))
                self.assertEqual(admin.execute("SELECT count(*) FROM nexus.outbox WHERE id=%s",(key,)).fetchone()[0],1)
                with self.assertRaises(psycopg.errors.InvalidParameterValue): g.request(rid,"enqueue",key,dict(payload,text="changed"))
                admin.execute("UPDATE nexus.preview_session SET starts_at=clock_timestamp()-interval '49 hours'")
                self.assertTrue(g.request(rid,"enqueue",key,payload))
                self.assertFalse(g.request(uuid.uuid4(),"enqueue",uuid.uuid4().hex,payload))
            finally:
                admin.execute("GRANT EXECUTE ON FUNCTION nexus.save_preview(text,jsonb),nexus.enqueue_preview(text,jsonb) TO nexus_preview")
