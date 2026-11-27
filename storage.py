"""Durable local SQLite preview queue; no publishing."""
import sqlite3, json
class Storage:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=10)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS drafts (url TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.db.commit()
    def save(self,draft):
        with self.db:
            return self.db.execute("INSERT OR IGNORE INTO drafts VALUES (?,?)",(draft["url"],json.dumps(draft,ensure_ascii=False))).rowcount==1
    def pending(self):
        return [json.loads(row[0]) for row in self.db.execute("SELECT payload FROM drafts ORDER BY rowid")]
    def close(self):
        self.db.close()
