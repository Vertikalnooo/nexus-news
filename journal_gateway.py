"""Explicit replay of identical request only; never retries automatically."""
import json,uuid
class JournalGateway:
    def __init__(self,connect): self.connect=connect
    def request(self,request_id,operation,key,payload):
        from psycopg.pq import TransactionStatus
        request_id=uuid.UUID(str(request_id))
        if operation not in ("save","enqueue") or not isinstance(key,str) or not 1<=len(key)<=2048 or not isinstance(payload,dict): raise ValueError("invalid request")
        body=json.dumps(payload,allow_nan=False,ensure_ascii=False)
        if len(body.encode())>65536: raise ValueError("oversize")
        with self.connect() as db:
            if not db.autocommit or db.info.transaction_status!=TransactionStatus.IDLE: raise ValueError("autocommit required")
            return db.execute("SELECT nexus.gateway_write(%s,%s,%s,%s::jsonb)",(request_id,operation,key,body)).fetchone()[0] is True
