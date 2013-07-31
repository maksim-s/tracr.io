class Annotation(object):
  """
  `app.trace.annotation.Annotation` is a top level class for any information
  that you want to store during a duration of a `app.trace.trace.Trace` or
  `app.trace.span.Span`
  """
  def __init__(self, span, data_dict):
    """
    :param span: `app.trace.span.Span` object
    :param data_dict: python dictionary that contains all the data to be
    stored.
    """
    self.span = span
    self.data = data_dict
