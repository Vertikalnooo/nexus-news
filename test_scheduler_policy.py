import unittest
from datetime import datetime,timezone,timedelta
from scheduler_policy import allowed
class SchedulerTests(unittest.TestCase):
    def test_limits(self):
        n=datetime.now(timezone.utc)
        self.assertFalse(allowed(n,n,0))
        self.assertFalse(allowed(n,None,24))
        self.assertTrue(allowed(n,n-timedelta(hours=1),23))
        self.assertFalse(allowed(n,n+timedelta(hours=1),0))
