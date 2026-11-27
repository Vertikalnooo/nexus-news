"""Conservative preview scheduling policy; no active scheduler."""
from datetime import datetime,timezone
MIN_INTERVAL_SECONDS=3600
MAX_DAILY_RUNS=24
MAX_DAILY_GEMINI_REQUESTS=0
def allowed(now,last_run,daily_runs):
    if now.tzinfo is None or (last_run is not None and last_run.tzinfo is None): return False
    if not 0<=daily_runs<MAX_DAILY_RUNS: return False
    return last_run is None or (now-last_run).total_seconds()>=MIN_INTERVAL_SECONDS
