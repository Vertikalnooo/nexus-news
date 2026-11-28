import os,socket,threading,unittest,json
from unittest.mock import Mock
from gateway_socket import serve_one
class SocketTests(unittest.TestCase):
    def test_protocol(self):
        gateway=Mock(); gateway.request.return_value=True
        a,b=socket.socketpair()
        with a,b:
            t=threading.Thread(target=serve_one,args=(a,gateway,os.getuid()))
            t.start()
            b.sendall(json.dumps(dict(request_id="id",operation="enqueue",key="key",payload={})).encode()+b"\n")
            self.assertEqual(json.loads(b.recv(4096)),{"status":"saved"})
            t.join(2)
        gateway.request.assert_called_once_with("id","enqueue","key",{})
    def test_wrong_peer(self):
        gateway=Mock()
        a,b=socket.socketpair()
        with a,b: serve_one(a,gateway,os.getuid()+1)
        gateway.request.assert_not_called()
