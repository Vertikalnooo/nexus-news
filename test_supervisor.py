import sys,unittest,time
from supervisor import supervise
class SupervisorTests(unittest.TestCase):
    def test_expired(self):
        self.assertEqual(supervise(["nonexistent"],0),124)
    def test_normal(self):
        self.assertEqual(supervise([sys.executable,"-c","pass"],2),0)
    def test_kill(self):
        start=time.monotonic()
        self.assertEqual(supervise([sys.executable,"-c","import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)"],.2),124)
        self.assertLess(time.monotonic()-start,3)
