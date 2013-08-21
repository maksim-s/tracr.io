import inspect
import re
import time

from functools import wraps

from django.conf import settings
from django.db import connection
from django.db.models import Model

from tracr.core.context import context

RELATED_ATTR_CLASS_RE = re.compile('^.*Objects?Descriptor')

def instrument_function(func):
  """
  Decorator to wrap a function call in a scope.
  """

  if inspect.isgeneratorfunction(func):
    # For now ignore generators.
    return func

  @wraps(func)
  def wrapper(*args, **kwargs):
    function_name = func.__name__
    module_name = func.__module__
    data = {'module': module_name}
    scope_name = function_name
    if hasattr(func, 'im_class'):
      # The function is a method of some class.
      class_name = func.im_class.__name__
      scope_name = '%s:%s' % (class_name, function_name)

    func_exception = None
    # TODO(maksims): Make sure that connections are not shared
    # between requests. Also Django only records queries if DEBUG
    #  is set to True, so we need to do something about it.
    start_queries = set(connection.queries)
    context.enter_scope(scope_name, data)
    try:
      return_value = func(*args, **kwargs)
    except Exception as e:
      context.update_scope_data('exception', e.__class__.__name__)
      func_exception = e
    end_queries = set(connection.queries)
    function_queries = end_queries - start_queries
    queries_time = sum(query['time'] for query in function_queries)
    query_data = {
        'total_number': len(function_queries),
        'total_time': queries_time
        }
    context.update_scope_data('db_queries', query_data)
    context.leave_scope()
    if func_exception:
      raise func_exception
    return return_value

  return wrapper

def _annotate_function(func, annotation_prefix):
  @wraps(func)
  def new_func(*args, **kwargs):
    start_time = time.time()
    raise_value = False
    try:
      value = func(*args, **kwargs)
    except Exception as e:
      value = e
      raise_value = True
    annotation_data = {
      'duration': time.time() - start_time,
      'module': func.__module__
      }
    if raise_value:
      annotation_data['exception'] = str(e)
    context.annotate('%s:%s' % (annotation_prefix, func.__name__),
                     annotation_data)
    if raise_value:
      raise value
    return value
  return new_func

def instrument_model(klass, **kwargs):
  if not issubclass(klass, Model):
    raise ValueError

  klass_name = klass.__name__

  # Annotate all save calls with their duration.
  klass.save = _annotate_function(klass.save, klass_name)

  # Annotate all *related* fields.
  for attr_name in dir(klass):
    attr = getattr(klass, attr_name)
    if getattr(attr, '__module__', None) != 'django.db.models.fields.related':
      continue
    attr_class_name = getattr(attr, '__class__', str).__name__
    if RELATED_ATTR_CLASS_RE.match(attr_class_name) is None:
      continue
    if hasattr(attr, 'get_queryset'):
      attr.get_queryset = _annotate_function(attr.get_queryset,
                                             '%s:%s' % (klass_name, attr_name))
      attr.get_prefetch_queryset = _annotate_function(
          attr.get_prefetch_queryset,
          '%s:%s' % (klass_name, attr_name))
    elif hasattr(attr, 'related_manager_cls'):
      attr.related_manager_cls.get_queryset = _annotate_function(
          attr.related_manager_cls.get_queryset,
          '%s:%s' % (klass_name, attr_name))
      attr.related_manager_cls.get_prefetch_queryset = _annotate_function(
          attr.related_manager_cls.get_prefetch_queryset,
          '%s:%s' % (klass_name, attr_name))

  return klass

class scope(object):
  def __init__(self, name, data=None):
    self._name = name
    self._data = data

  def __enter__(self):
    scope = context.enter_scope(self._name, data=self._data)
    return scope

  def __exit__(self, *args, **kwargs):
    context.leave_scope()
