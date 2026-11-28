"""Offline subprocess gateway; credentials supplied only to gateway process."""
import os,sys,json
from write_gateway import WriteGateway
def main():
    import psycopg
    dsn=os.environ.pop("NEXUS_GATEWAY_DSN")
    if os.getenv("NEXUS_DATABASE_URL"): raise ValueError("mixed credentials")
    gateway=WriteGateway(lambda:psycopg.connect(dsn,sslmode="verify-full",autocommit=True,connect_timeout=10))
    while True:
        line=sys.stdin.buffer.readline(131073)
        if not line: return
        if len(line)>131072 or not line.endswith(b"\n"): return
        try:
            req=json.loads(line)
            if set(req)!={"operation","key","payload"}: raise ValueError()
            result=gateway.request(req["operation"],req["key"],req["payload"])
            reply={"status":"saved" if result else "denied"}
        except (ValueError,TypeError,KeyError): reply={"status":"invalid"}
        except Exception: reply={"status":"unknown"}
        print(json.dumps(reply),flush=True)
if __name__=="__main__": main()
