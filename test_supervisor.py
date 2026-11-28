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

    def test_parent_crash(self):
        import subprocess, tempfile, pathlib, os, signal
        with tempfile.TemporaryDirectory() as tmp:
            marker=pathlib.Path(tmp)/"child"
            code="import os,time,pathlib; pathlib.Path("+repr(str(marker))+").write_text(str(os.getpid())); time.sleep(30)"
            parent=subprocess.Popen([sys.executable,"-c","from supervisor import supervise; import sys; supervise([sys.executable,'-c',"+repr(code)+"],30)"])
            try:
                for _ in range(100):
                    if marker.exists() and marker.read_text(): break
                    time.sleep(.02)
                pid=int(marker.read_text())
                parent.kill(); parent.wait(timeout=3)
                for _ in range(100):
                    try: state=pathlib.Path(f"/proc/{pid}/stat").read_text().split(") ")[1][0]
                    except FileNotFoundError: break
                    if state=="Z": break
                    time.sleep(.02)
                else: self.fail("child survived supervisor crash")
            finally:
                if parent.poll() is None: parent.kill(); parent.wait()
