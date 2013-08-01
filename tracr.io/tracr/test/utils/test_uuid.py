import time
import unittest

from tracr.utils.uuid import uuid1


class TestUUID(unittest.TestCase):
  def test_uuid1(self):
    t1 = time.time()
    uuid_1 = uuid1(t1)
    time.sleep(0.1)
    t2 = time.time()
    uuid_2 = uuid1(t2)
    delta1 = uuid_1.time - int(1e7 * t1)
    delta2 = uuid_2.time - int(1e7 * t2)
    # Check that time is correlated with uuid1.
    self.assertTrue((delta1 - delta2) < 10)
    # Check that we have time granularity.
    self.assertNotEqual(uuid_1.time, uuid_2.time)
