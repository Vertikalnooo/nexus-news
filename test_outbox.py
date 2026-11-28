import tempfile,unittest
from pathlib import Path
from outbox import Outbox
class OutboxTests(unittest.TestCase):
    def test_restart_and_switch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"queue.db"
            q=Outbox(p)
            preview=dict(mode="dry-run",sent=False,text="test")
            key=q.enqueue("draft",preview)
            calls=[]
            def api(x): calls.append(x); return "mock-1"
            self.assertEqual(q.dispatch(key,api),"disabled")
            self.assertEqual(q.dispatch(key,api,enabled=True,approved=True),"simulated")
            q.close()
            q=Outbox(p)
            self.assertEqual(q.enqueue("draft",preview),key)
            self.assertEqual(q.dispatch(key,api,enabled=True,approved=True),"blocked")
            self.assertEqual(len(calls),1)
            q.close()
    def test_unknown_no_retry(self):
        q=Outbox(":memory:")
        key=q.enqueue("draft",dict(mode="dry-run",sent=False))
        def fail(x): raise TimeoutError()
        self.assertEqual(q.dispatch(key,fail,enabled=True,approved=True),"unknown")
        self.assertEqual(q.dispatch(key,fail,enabled=True,approved=True),"blocked")
        q.close()
