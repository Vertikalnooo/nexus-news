import unittest,os,uuid,secrets,hashlib
from unittest.mock import MagicMock,patch
from types import ModuleType,SimpleNamespace
import sys
class GatewayFaultTests(unittest.TestCase):
    def test_ambiguous_commit_no_retry(self):
        from write_gateway import WriteGateway
        driver=ModuleType('psycopg'); pq=ModuleType('psycopg.pq')
        pq.TransactionStatus=SimpleNamespace(IDLE=0)
        driver.OperationalError=type('OperationalError',(Exception,),{})
        db=MagicMock(); db.autocommit=True; db.info.transaction_status=pq.TransactionStatus.IDLE
        db.__enter__.return_value=db
        db.execute.side_effect=driver.OperationalError("synthetic lost commit response")
        connect=MagicMock(return_value=db)
        with patch.dict(sys.modules,{'psycopg':driver,'psycopg.pq':pq}), self.assertRaises(driver.OperationalError):
            WriteGateway(connect).request("enqueue","key",{"mode":"dry-run","sent":False})
        self.assertEqual(db.execute.call_count,1)
        self.assertEqual(connect.call_count,1)
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class ExpiryTests(unittest.TestCase):
    def test_expired_capability(self):
        import psycopg
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as db:
            key=uuid.uuid4().hex; token=secrets.token_bytes(32)
            db.execute("DELETE FROM nexus.preview_session")
            db.execute("INSERT INTO nexus.preview_session(singleton,starts_at,runs) VALUES(true,clock_timestamp(),1)")
            db.execute("INSERT INTO nexus.outbox(id,payload,state,claim_hash,claim_until) VALUES(%s,'{}','unknown',%s,clock_timestamp()-interval '1 second')",(key,hashlib.sha256(token).digest()))
            db.execute("UPDATE nexus.publication_control SET enabled=true")
            try:
                db.execute("SET ROLE nexus_mock_worker")
                self.assertFalse(db.execute("SELECT nexus.finish_mock(%s,%s,'mock-1')",(key,token)).fetchone()[0])
            finally:
                db.execute("RESET ROLE")
                db.execute("UPDATE nexus.publication_control SET enabled=false")
