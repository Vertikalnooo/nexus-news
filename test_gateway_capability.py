import os,unittest,uuid,hashlib,secrets
from concurrent.futures import ThreadPoolExecutor
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class GatewayCapabilityTests(unittest.TestCase):
    def connect(self):
        import psycopg
        return psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True)
    def test_capability(self):
        from write_gateway import WriteGateway
        key=uuid.uuid4().hex
        def gateway_connect():
            db=self.connect(); db.execute("SET ROLE nexus_preview"); return db
        gateway=WriteGateway(gateway_connect)
        with self.connect() as admin:
            admin.execute("DELETE FROM nexus.preview_session")
            admin.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1)")
            self.assertTrue(gateway.request("enqueue",key,{"mode":"dry-run","sent":False}))
            with self.assertRaises(ValueError): gateway.request("COMMIT",key,{})
            admin.execute("UPDATE nexus.publication_control SET enabled=true")
            try:
                token=secrets.token_bytes(32)
                with self.connect() as db:
                    db.execute("SET ROLE nexus_mock_worker")
                    self.assertIsNotNone(db.execute("SELECT nexus.claim_mock(%s,%s)",(key,hashlib.sha256(token).digest())).fetchone()[0])
                    self.assertFalse(db.execute("SELECT nexus.finish_mock(%s,%s,'mock-1')",(key,secrets.token_bytes(32))).fetchone()[0])
                def finish(_):
                    with self.connect() as db:
                        db.execute("SET ROLE nexus_mock_worker")
                        return db.execute("SELECT nexus.finish_mock(%s,%s,'mock-1')",(key,token)).fetchone()[0]
                with ThreadPoolExecutor(max_workers=8) as pool: self.assertEqual(sum(pool.map(finish,range(8))),1)
                self.assertFalse(finish(0))
            finally: admin.execute("UPDATE nexus.publication_control SET enabled=false")
