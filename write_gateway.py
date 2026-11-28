"""Offline gateway core: fixed operations, no caller SQL or transaction control."""
import json
class WriteGateway:
    def __init__(self,connect): self._connect=connect
    def request(self,operation,key,payload):
        if operation not in ("save","enqueue") or not isinstance(key,str) or not 1<=len(key)<=2048 or not isinstance(payload,dict): raise ValueError("invalid request")
        body=json.dumps(payload,ensure_ascii=False,allow_nan=False)
        if len(body.encode())>65536: raise ValueError("oversize")
        sql={"save":"SELECT nexus.save_preview(%s,%s::jsonb)","enqueue":"SELECT nexus.enqueue_preview(%s,%s::jsonb)"}[operation]
        from psycopg.pq import TransactionStatus
        with self._connect() as db:
            if not db.autocommit or db.info.transaction_status!=TransactionStatus.IDLE: raise ValueError("autocommit required")
            return db.execute(sql,(key,body)).fetchone()[0] is True
