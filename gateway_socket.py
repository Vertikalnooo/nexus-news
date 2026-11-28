"""Linux local gateway. Socket directory must be provisioned by trusted operator."""
import os,socket,struct,json,stat
def serve_one(conn,gateway,uid):
    conn.settimeout(5)
    _,peer,_=struct.unpack("3i",conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if peer!=uid: return
    with conn.makefile("rb") as stream: line=stream.readline(131073)
    if len(line)>131072 or not line.endswith(b"\n"): return
    try:
        req=json.loads(line)
        if not isinstance(req,dict) or set(req)!={"request_id","operation","key","payload"}: raise ValueError()
        result=gateway.request(req["request_id"],req["operation"],req["key"],req["payload"])
        reply={"status":"saved" if result else "denied"}
    except (ValueError,TypeError): reply={"status":"invalid"}
    except Exception: reply={"status":"unknown"}
    conn.sendall(json.dumps(reply).encode()+b"\n")
def main():
    import psycopg
    from journal_gateway import JournalGateway
    dsn=os.environ.pop("NEXUS_GATEWAY_DSN")
    if os.getenv("NEXUS_DATABASE_URL"): raise ValueError("mixed credentials")
    path=os.environ["NEXUS_GATEWAY_SOCKET"]; uid=int(os.environ["NEXUS_WORKER_UID"])
    if uid==os.getuid(): raise ValueError("separate OS identities required")
    parent=os.stat(os.path.dirname(path))
    if parent.st_uid!=os.getuid() or parent.st_mode & 0o022: raise ValueError("unsafe socket directory")
    gateway=JournalGateway(lambda:psycopg.connect(dsn,sslmode="verify-full",autocommit=True,connect_timeout=10,options="-c statement_timeout=10000"))
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        old=os.umask(0o117)
        try: server.bind(path)
        finally: os.umask(old)
        try:
            server.listen(8)
            while True:
                conn,_=server.accept()
                with conn:
                    try: serve_one(conn,gateway,uid)
                    except OSError: pass
        finally: os.unlink(path)
if __name__=="__main__": main()
