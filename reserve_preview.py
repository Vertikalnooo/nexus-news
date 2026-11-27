"""Reserve before expensive dependencies; standalone diagnostic, no scheduling."""
import os
from cloud_storage import PostgresStorage
def main():
    if os.getenv("NEXUS_PREVIEW_ENABLED")!="true": raise SystemExit("preview disabled")
    s=PostgresStorage(os.environ["NEXUS_DATABASE_URL"])
    try:
        if not s.reserve_run(): raise SystemExit("budget denied")
    finally: s.close()
if __name__=="__main__": main()
