from __future__ import absolute_import

from datetime import datetime
from time import mktime
from uuid import UUID, uuid4


def uuid1(time=None):
  # Generate uuid based on utc, instead of machine clock
  nanoseconds = int((time or mktime(datetime.utcnow().timetuple())) * 1e9)

  # 0x01b21dd213814000 is the number of 100-ns intervals between the
  # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
  timestamp = int(nanoseconds // 100) + 0x01b21dd213814000L

  time_low = timestamp & 0xffffffffL
  time_mid = (timestamp >> 32L) & 0xffffL
  time_hi_version = (timestamp >> 48L) & 0x0fffL

  random_uuid = uuid4()
  clock_seq_low = random_uuid.clock_seq_low
  clock_seq_hi_variant = random_uuid.clock_seq_hi_variant
  node = random_uuid.node

  return UUID(fields=(time_low, time_mid, time_hi_version,
                      clock_seq_hi_variant, clock_seq_low, node),
              version=1)
