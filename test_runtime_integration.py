import os,unittest
from unittest.mock import patch
from datetime import datetime,timezone
import runtime
@unittest.skipUnless(os.getenv("NEXUS_TEST_DSN"),"integration only")
class RuntimeIntegration(unittest.TestCase):
    def test_preview_to_outbox(self):
        import psycopg
        from cloud_storage import PostgresStorage
        from email.utils import format_datetime
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as admin:
            admin.execute("DELETE FROM nexus.run_budget")
            admin.execute("UPDATE nexus.publication_control SET enabled=false")
        store=PostgresStorage(os.environ["NEXUS_TEST_DSN"])
        store.db.execute("SET ROLE nexus_preview")
        stamp=format_datetime(datetime.now(timezone.utc))
        rss=("<rss><channel><item><title>Bitcoin central bank interest rates</title><link>https://example.org/runtime-integration</link><pubDate>"+stamp+"</pubDate></item></channel></rss>").encode()
        with patch.dict(os.environ,{"NEXUS_PREVIEW_START_UTC":datetime.now(timezone.utc).isoformat(),"NEXUS_PREVIEW_ENABLED":"true","NEXUS_PREPARE_MODEL":"false","NEXUS_DATABASE_URL":os.environ["NEXUS_TEST_DSN"],"NEXUS_OPUS_MODEL":"mock"}),patch.object(runtime,"PostgresStorage",return_value=store),patch.object(runtime,"Opus",return_value=lambda x:"Центральный банк и биткоин"),patch.object(runtime,"fetch",return_value=rss):
            runtime.main()
        with psycopg.connect(os.environ["NEXUS_TEST_DSN"],sslmode="verify-full",autocommit=True) as admin:
            self.assertGreater(admin.execute("SELECT count(*) FROM nexus.outbox WHERE state='pending' AND payload->>'text' LIKE '%Центральный банк и биткоин%'").fetchone()[0],0)
            self.assertFalse(admin.execute("SELECT enabled FROM nexus.publication_control").fetchone()[0])
