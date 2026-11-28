"""Mock-only persistent outbox; never imports a network transport."""
import json,hashlib
class MockTelegram:
    def __init__(self, outcome="ok"):
        self.outcome=outcome
        self.calls=0
    def send(self,payload):
        self.calls+=1
        if self.outcome!="ok": raise RuntimeError("simulated "+self.outcome)
        return "mock-"+str(self.calls)
class PgOutbox:
    def __init__(self,db): self.db=db
    def enqueue(self,draft_id,preview):
        if not draft_id or preview.get("sent") is not False or preview.get("mode")!="dry-run": raise ValueError("invalid preview")
        key=hashlib.sha256(draft_id.encode()).hexdigest()
        with self.db.transaction():
            if not self.db.execute("SELECT nexus.enqueue_preview(%s,%s::jsonb)",(key,json.dumps(preview))).fetchone()[0]: return None
        return key
    def dispatch(self,key,api,*,approved=False):
        if type(api) is not MockTelegram or approved is not True: return "disabled"
        with self.db.transaction():
            enabled=self.db.execute("SELECT nexus.lock_publication_switch()").fetchone()
            if not enabled or not enabled[0]: return "disabled"
            row=self.db.execute("UPDATE nexus.outbox SET state='unknown' WHERE id=%s AND state='pending' RETURNING payload",(key,)).fetchone()
        if row is None: return "blocked"
        with self.db.transaction():
            enabled=self.db.execute("SELECT nexus.lock_publication_switch()").fetchone()
            if not enabled or not enabled[0]: return "unknown"
            try: result=api.send(row[0])
            except Exception: return "unknown"
            self.db.execute("UPDATE nexus.outbox SET state='simulated',message_id=%s WHERE id=%s AND state='unknown'",(result,key))
        return "simulated"
