import json
import thread

from functools import wraps

from tracr.conf import constants
from tracr.core.exceptions import (ContextMissing,
                                   NoActiveScope)
from tracr.trace import Trace


def current_thread_id():
  # TODO(usmanm): This assumes gevent.monket.patch_thread() has been called.
  # Can we avoid this? Basically we want to check if we're executing in a
  # greenlet.
  return thread.get_ident()


class Context(object):
  REQUIRED_KEYS = {'tid', 'sid'} # Keys required in the HTTP header.

  def __init__(self, thread_id, request):
    self._request = request
    tracr_metadata = json.loads(request.META.get(constants.HTTP_HEADER,
                                                 '{}'))
    if Context.REQUIRED_KEYS <= set(tracr_metadata):
      self._trace = Trace(trace_id=tracr_metadata['tid'],
                          parent_scope_id=tracr_metadata['sid'])
    else:
      # No trace data found in the request. Create a new trace.
      self._trace = Trace()
    self._thread_id = thread_id
    self._active_scope = None

  def ensure_active_scope(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
      if not self._active_scope:
        raise NoActiveScope
      return method(self, *args, **kwargs)
    return wrapper

  def get_thread_id(self):
    return self._thread_id

  def get_trace(self):
    return self._trace

  def enter_scope(self, name, data=None):
    if self._active_scope:
      scope = self._active_scope.add_child(name, data=data)
    else:
      scope = self._trace.create_scope(name, data=data)
    scope.start()
    self._active_scope = scope

  @ensure_active_scope
  def leave_scope(self):
    self._active_scope.end()
    self._active_scope = self._active_scope.get_parent()

  @ensure_active_scope
  def update_scope_data(self, key, value):
    self._active_scope.update_data(key, value)

  @ensure_active_scope
  def annotate(self, name, data=None):
    self._active_scope.add_annotation(name, data=data)

  def mark(self, name):
    self._trace.add_mark(name)


class ContextManager(object):
  def __init__(self):
    self._thread_id_to_context = {}

  def create_context(self, request):
    thread_id = current_thread_id()
    context = Context(thread_id, request)
    self._thread_id_to_context[thread_id] = context
    return context

  def get_context(self):
    return self._thread_id_to_context.get(current_thread_id())

manager = ContextManager()


class ActiveContext(Context):
  def __init__(self):
    pass

  def __getattr__(self, attr):
    context = manager.get_context()
    if not context:
      raise ContextMissing
    return getattr(context, attr)

  def __setattr__(self, attr, value):
    context = manager.get_context()
    if not context:
      raise ContextMissing
    return setattr(context, attr, value)

context = ActiveContext()
