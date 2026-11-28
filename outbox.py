"""SQLite reference outbox; no real Telegram transport."""
import sqlite3, hashlib, json
class Outbox:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=10)
        self.db.execute("CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL, message_id TEXT)")
        self.db.commit()
    def enqueue(self,draft_id,preview):
        if not draft_id or preview.get("sent") is not False or preview.get("mode")!="dry-run": raise ValueError("invalid preview")
        key=hashlib.sha256(draft_id.encode()).hexdigest()
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO outbox VALUES(?,?,'pending',NULL)",(key,json.dumps(preview)))
        return key
    def dispatch(self,key,api,*,enabled=False,approved=False):
        if enabled is not True or approved is not True: return "disabled"
        with self.db:
            row=self.db.execute("UPDATE outbox SET state='unknown' WHERE id=? AND state='pending' RETURNING payload",(key,)).fetchone()
        if row is None: return "blocked"
        try:
            result=api(json.loads(row[0]))
            if not isinstance(result,str) or not result: return "unknown"
        except Exception: return "unknown"
        with self.db:
            self.db.execute("UPDATE outbox SET state='simulated',message_id=? WHERE id=? AND state='unknown'",(result,key))
        return "simulated"
    def close(self): self.db.close()
