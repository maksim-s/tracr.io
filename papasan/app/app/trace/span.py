class Span(object):
  """
  `app.trace.span.Span` record all the information related to the timing in a
  `app.trace.trace.Trace`.
  """
  def __init__(self, start_time, end_time, trace, parent=None):
    self.start_time = start_time
    self.end_time = end_time
    self.parent = parent
    self.trace = trace
