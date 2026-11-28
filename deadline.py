"""Linux main-thread deadline; fail closed, never swallowed by except Exception."""
import math,signal,time
from contextlib import contextmanager
class DeadlineExpired(BaseException): pass
@contextmanager
def deadline(seconds):
    if not math.isfinite(seconds) or seconds<=0: raise DeadlineExpired()
    if signal.getitimer(signal.ITIMER_REAL)[0]: raise RuntimeError("existing timer")
    def expire(*_): raise DeadlineExpired()
    old=signal.signal(signal.SIGALRM,expire)
    try:
        signal.setitimer(signal.ITIMER_REAL,seconds)
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        signal.signal(signal.SIGALRM,old)
