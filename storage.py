"""Durable local SQLite preview queue; no publishing."""
import sqlite3, json
class Storage:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=10)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS drafts (url TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS draft_title_key ON drafts(json_extract(payload,'$.title_key'))")
        self.db.commit()
    def contains(self,url,key):
        return self.db.execute("SELECT 1 FROM drafts WHERE url=? OR json_extract(payload,'$.title_key')=?",(url,key)).fetchone() is not None
    def save(self,draft):
        with self.db:
            return self.db.execute("INSERT OR IGNORE INTO drafts VALUES (?,?)",(draft["url"],json.dumps(draft,ensure_ascii=False))).rowcount==1
    def pending(self):
        return [json.loads(row[0]) for row in self.db.execute("SELECT payload FROM drafts ORDER BY rowid")]
    def close(self):
        self.db.close()
