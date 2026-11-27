"""PostgreSQL draft queue; explicit DSN, no provisioning."""
import json
class PostgresStorage:
    def __init__(self,dsn):
        import psycopg
        self.db=psycopg.connect(dsn,sslmode="verify-full",connect_timeout=10)
    def reserve_run(self):
        with self.db.transaction():
            row=self.db.execute("""
                INSERT INTO nexus.run_budget AS b (singleton,last_run,day_utc,runs)
                VALUES (true,statement_timestamp(),(statement_timestamp() AT TIME ZONE 'UTC')::date,1)
                ON CONFLICT (singleton) DO UPDATE SET
                    last_run=EXCLUDED.last_run,
                    day_utc=EXCLUDED.day_utc,
                    runs=CASE WHEN b.day_utc=EXCLUDED.day_utc THEN b.runs+1 ELSE 1 END
                WHERE EXCLUDED.last_run >= b.last_run + interval '1 hour'
                  AND EXCLUDED.day_utc >= b.day_utc
                  AND (b.day_utc<>EXCLUDED.day_utc OR b.runs<24)
                RETURNING runs
            """).fetchone()
            return row is not None
    def save(self,draft):
        with self.db.transaction():
            return self.db.execute("INSERT INTO nexus.drafts (url,payload) VALUES (%s,%s::jsonb) ON CONFLICT (url) DO NOTHING",(draft["url"],json.dumps(draft,ensure_ascii=False))).rowcount==1
    def pending(self):
        return [row[0] for row in self.db.execute("SELECT payload FROM nexus.drafts ORDER BY created_at,url")]
    def close(self):
        self.db.close()
