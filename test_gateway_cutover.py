import os,unittest,uuid
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class CutoverTests(unittest.TestCase):
    def test_permissions(self):
        import psycopg
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as db:
            for role in ("nexus_preview","nexus_write_gateway"):
                db.execute("SET ROLE "+role)
                with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute("SELECT nexus.enqueue_preview('blocked','{}')")
                db.execute("RESET ROLE")
            db.execute("SET ROLE nexus_preview")
            with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute("SELECT nexus.gateway_write(%s,'enqueue','blocked','{}')",(uuid.uuid4(),))
            db.execute("RESET ROLE")
