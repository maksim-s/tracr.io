import time

from functools import wraps

from django.dispatch import Signal

from tracr.core.context import manager
from tracr.utils.inspect import get_stack


class Signal(Signal):
  def __init__(self, enable_stack=False):
    self.enable_stack = enable_stack
    super(Signal, self).__init__(
        providing_args=['duration', 'args', 'kwargs', 'exception', 'value',
                        'stack', 'context'])

  def dispatch(self):
    def decorator(func):
      @wraps(func)
      def wrapper(*args, **kwargs):
        start_time = time.time()
        exception = None
        value = None
        try:
          value = func(*args, **kwargs)
        except Exception, e:
          exception = e
        duration = time.time() - start_time
        kwargs = {
          'sender': func,
          'duration': duration,
          'args': args,
          'kwargs': kwargs,
          'exception': exception,
          'value': value,
          'stack': get_stack() if self.enable_stack else None,
          'context': manager.get_context()
          }
        self.send(**kwargs)
        if exception:
          raise exception
        return value
      return wrapper
    return decorator


class Handler(object):
  def __init__(self, *args, **kwargs):
    pass

  def process_request(self, request):
    pass

  def process_view(self, request, view_func, view_args, view_kwargs):
    pass

  def process_template_response(self, request, response):
    pass

  def process_response(self, request, response):
    pass

  def process_exception(self, request, exception):
    pass
