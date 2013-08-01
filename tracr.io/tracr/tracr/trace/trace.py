from tracr.utils.uuid import uuid1


class Trace(object):
  """
  `tracr.trace.trace.Trace` is the top level object that monitors the request
  behavior.
  """
  def __init__(self, trace_id=None):
    self.id = trace_id or uuid1()
