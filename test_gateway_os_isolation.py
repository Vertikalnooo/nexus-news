import os,socket,subprocess,sys,tempfile,unittest,threading
from unittest.mock import Mock
from gateway_socket import serve_one
@unittest.skipUnless(sys.platform=="linux" and os.getuid()==0,"requires isolated root test runner")
class OSIsolationTests(unittest.TestCase):
    def test_distinct_uid(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.chmod(tmp,0o755)
            path=tmp+"/gateway.sock"
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
                server.bind(path); os.chmod(path,0o666); server.listen(2); server.settimeout(5)
                gateway=Mock(); gateway.request.return_value=True
                code="import socket,sys; s=socket.socket(socket.AF_UNIX); s.settimeout(3); s.connect(sys.argv[1]); s.sendall(b'{\"request_id\":\"id\",\"operation\":\"enqueue\",\"key\":\"key\",\"payload\":{}}\\n'); print(s.recv(4096))"
                for uid in (65534,65533):
                    child=subprocess.Popen([sys.executable,"-c",code,path],user=uid,group=uid,extra_groups=[],env={"PATH":"/usr/bin:/bin"},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    try:
                        conn,_=server.accept()
                        with conn: serve_one(conn,gateway,65534)
                        out,err=child.communicate(timeout=5)
                        if uid==65534: self.assertIn(b"saved",out)
                        else: self.assertNotIn(b"saved",out)
                    finally:
                        if child.poll() is None: child.kill(); child.wait()
                gateway.request.assert_called_once()
