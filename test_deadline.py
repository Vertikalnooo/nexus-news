import signal,time,unittest
from deadline import deadline,DeadlineExpired
class DeadlineTests(unittest.TestCase):
    def test_expired(self):
        with self.assertRaises(DeadlineExpired):
            with deadline(0): self.fail("entered expired window")
    def test_interrupt(self):
        with self.assertRaises(DeadlineExpired):
            with deadline(.03):
                try: time.sleep(1)
                except Exception: self.fail("deadline swallowed")
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0],0)
    def test_cleanup(self):
        with deadline(1): pass
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0],0)
