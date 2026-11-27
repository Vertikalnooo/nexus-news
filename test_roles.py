import os,unittest
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class RoleTests(unittest.TestCase):
    def test_permissions(self):
        import psycopg
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as db:
            db.execute("SET ROLE nexus_preview")
            for sql in ("DELETE FROM nexus.drafts","UPDATE nexus.run_budget SET runs=1","SELECT * FROM nexus.run_budget","CREATE TABLE nexus.forbidden(x int)"):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute(sql)
            self.assertIsInstance(db.execute("SELECT nexus.reserve_run()").fetchone()[0],bool)
            db.execute("SELECT * FROM nexus.drafts LIMIT 1")

    def test_owner_isolation(self):
        import psycopg
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as db:
            owner=db.execute("SELECT r.rolname,r.rolsuper,r.rolcanlogin,r.rolcreaterole,r.rolbypassrls FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner WHERE p.oid='nexus.reserve_run()'::regprocedure").fetchone()
            self.assertEqual(owner,("nexus_budget_owner",False,False,False,False))
            db.execute("SET ROLE nexus_budget_owner")
            for sql in ("SELECT * FROM nexus.drafts","DELETE FROM nexus.run_budget","CREATE TABLE nexus.forbidden(x int)"):
                with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute(sql)
