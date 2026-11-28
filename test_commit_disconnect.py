import os,uuid,unittest
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class DisconnectTests(unittest.TestCase):
    def test_disconnect_before_commit_and_reconcile(self):
        import psycopg
        from journal_gateway import JournalGateway
        def connect(): return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
        def gateway_connect():
            db=connect(); db.execute("SET ROLE nexus_write_gateway"); return db
        key=uuid.uuid4().hex; rid=uuid.uuid4(); payload='{"mode":"dry-run","sent":false}'
        with connect() as admin:
            admin.execute("DELETE FROM nexus.preview_session")
            admin.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1)")
            with gateway_connect() as db:
                db.execute("BEGIN")
                self.assertTrue(db.execute("SELECT nexus.gateway_write(%s,'enqueue',%s,%s::jsonb)",(rid,key,payload)).fetchone()[0])
                admin.execute("SELECT pg_terminate_backend(%s)",(db.info.backend_pid,))
                with self.assertRaises(psycopg.Error): db.execute("COMMIT")
            self.assertIsNone(admin.execute("SELECT request_id FROM nexus.gateway_journal WHERE request_id=%s",(rid,)).fetchone())
            gateway=JournalGateway(gateway_connect)
            self.assertTrue(gateway.request(rid,"enqueue",key,{"mode":"dry-run","sent":False}))
            self.assertTrue(gateway.request(rid,"enqueue",key,{"mode":"dry-run","sent":False}))
            self.assertEqual(admin.execute("SELECT count(*) FROM nexus.outbox WHERE id=%s",(key,)).fetchone()[0],1)
