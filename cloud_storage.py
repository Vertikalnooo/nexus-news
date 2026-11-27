"""PostgreSQL draft queue; explicit DSN, no provisioning."""
import json
class PostgresStorage:
    def __init__(self,dsn):
        import psycopg
        self.db=psycopg.connect(dsn,sslmode="verify-full",connect_timeout=10)
    def save(self,draft):
        with self.db.transaction():
            return self.db.execute("INSERT INTO nexus.drafts (url,payload) VALUES (%s,%s::jsonb) ON CONFLICT (url) DO NOTHING",(draft["url"],json.dumps(draft,ensure_ascii=False))).rowcount==1
    def pending(self):
        return [row[0] for row in self.db.execute("SELECT payload FROM nexus.drafts ORDER BY created_at,url")]
    def close(self):
        self.db.close()
