"""Linux preview supervisor; no scheduler activation."""
import os,signal,subprocess,sys,time,ctypes
def supervise(argv,seconds):
    if seconds<=0: return 124
    parent=os.getpid()
    def bind_parent():
        libc=ctypes.CDLL(None,use_errno=True)
        if libc.prctl(1,signal.SIGKILL,0,0,0)!=0 or os.getppid()!=parent: os._exit(125)
    child=subprocess.Popen(argv,start_new_session=True,preexec_fn=bind_parent)
    try:
        return child.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        return 124
    finally:
        try: os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError: pass
        child.wait()
def main():
    if os.getenv("NEXUS_PREVIEW_ENABLED")!="true": return 1
    from cloud_storage import PostgresStorage
    before=time.monotonic()
    store=PostgresStorage(os.environ["NEXUS_DATABASE_URL"])
    try: remaining=store.db.execute("SELECT nexus.preview_remaining()").fetchone()[0]
    finally: store.close()
    return supervise([sys.executable,"runtime.py"],min(540,remaining-(time.monotonic()-before)))
if __name__=="__main__": sys.exit(main())
