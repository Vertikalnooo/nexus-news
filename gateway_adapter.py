"""Pipeline adapter for a trusted gateway transport; no database write credentials."""
import uuid,hashlib,json
class GatewayAdapter:
    def __init__(self,reader,request): self.reader=reader; self.request=request
    def contains(self,url,key): return self.reader.contains(url,key)
    def pending(self): return self.reader.pending()
    def _write(self,op,key,payload):
        identity=json.dumps([op,key,payload],sort_keys=True,ensure_ascii=False,allow_nan=False)
        request_id=uuid.uuid5(uuid.NAMESPACE_URL,identity)
        return self.request(request_id,op,key,payload)
    def save(self,draft): return self._write("save",draft["url"],draft)
    def enqueue(self,draft_id,preview):
        key=hashlib.sha256(draft_id.encode()).hexdigest()
        return key if self._write("enqueue",key,preview) else None
