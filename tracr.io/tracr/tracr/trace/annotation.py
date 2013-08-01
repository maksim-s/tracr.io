class Annotation(object):
  """
  `tracr.trace.annotation.Annotation` is a top level class for any information
  that you want to store during a duration of a `tracr.trace.trace.Trace` or
  `tracr.trace.span.Span`
  """
  def __init__(self, span, data_dict):
    """
    :param span: `tracr.trace.span.Span` object
    :param data_dict: python dictionary that contains all the data to be
    stored.
    """
    self.span = span
    self.data = data_dict
