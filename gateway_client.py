"""One request per externally provisioned Unix socket connection."""
import socket,json
class GatewayUnknown(RuntimeError): pass
def request(request_id,operation,key,payload):
    import os
    body=json.dumps(dict(request_id=str(request_id),operation=operation,key=key,payload=payload),allow_nan=False).encode()+b"\n"
    if len(body)>131072: raise ValueError("oversize")
    try:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
            sock.settimeout(15)
            sock.connect(os.environ["NEXUS_GATEWAY_SOCKET"])
            sock.sendall(body)
            with sock.makefile("rb") as stream: reply=json.loads(stream.readline(4096))
    except (OSError,ValueError) as exc: raise GatewayUnknown("unconfirmed request "+str(request_id)) from exc
    if reply.get("status")=="saved": return True
    if reply.get("status")=="denied": return False
    raise GatewayUnknown("unconfirmed request "+str(request_id))
