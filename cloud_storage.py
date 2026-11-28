"""PostgreSQL draft queue; explicit DSN, no provisioning."""
import json
class PostgresStorage:
    def __init__(self,dsn):
        import psycopg
        self.db=psycopg.connect(dsn,sslmode="verify-full",connect_timeout=10,autocommit=True)
    def reserve_run(self):
        with self.db.transaction():
            return self.db.execute("SELECT nexus.reserve_run()").fetchone()[0]
    def contains(self,url,key):
        return self.db.execute("SELECT 1 FROM nexus.drafts WHERE url=%s OR payload->>'title_key'=%s",(url,key)).fetchone() is not None
    def save(self,draft):
        with self.db.transaction():
            return self.db.execute("SELECT nexus.save_preview(%s,%s::jsonb)",(draft["url"],json.dumps(draft,ensure_ascii=False))).fetchone()[0]
    def pending(self):
        return [row[0] for row in self.db.execute("SELECT payload FROM nexus.drafts ORDER BY created_at,url")]
    def close(self):
        self.db.close()
