import inspect
import re
import time

from functools import wraps

from django.db import connection
from django.db.models import Model

import tracr

from tracr.core.exceptions import TypeNotInstrumentable

RELATED_ATTR_CLASS_RE = re.compile('^.*Objects?Descriptor')


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
      '$duration': time.time() - start_time,
      '$module': func.__module__
      }
    if raise_value:
      annotation_data['$exception'] = str(e)
    tracr.annotate('%s:%s' % (annotation_prefix, func.__name__),
                   annotation_data)
    if raise_value:
      raise value
    return value
  return new_func


def _instrument_function(func, **kwargs):
  """
  Decorator to wrap a function call in a scope.
  """
  @wraps(func)
  def wrapper(*args, **kwargs):
    function_name = func.__name__
    data = {'$module': func.__module__}
    scope_name = function_name
    if hasattr(func, 'im_class'):
      # The function is a method of some class.
      class_name = func.im_class.__name__
      scope_name = '%s:%s' % (class_name, function_name)

    func_exception = None
    # TODO(maksims): Make sure that connections are not shared
    # between requests. Also Django only records queries if DEBUG
    # is set to True, so we need to do something about it.
    start_queries = set(connection.queries)
    tracr.enter_scope(scope_name, data)
    try:
      return_value = func(*args, **kwargs)
    except Exception as e:
      tracr.update_scope_data('$exception', str(e))
      func_exception = e
    end_queries = set(connection.queries)
    function_queries = end_queries - start_queries
    queries_time = sum(query['time'] for query in function_queries)
    query_data = {
        'total_number': len(function_queries),
        'total_time': queries_time
        }
    tracr.update_scope_data('db_queries', query_data)
    tracr.leave_scope()
    if func_exception:
      raise func_exception
    return return_value

  return wrapper


def _instrument_model(klass, **kwargs):
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


def instrument(obj, **kwargs):
  if inspect.isclass(obj) and issubclass(obj, Model):
    return _instrument_model(obj, **kwargs)
  elif inspect.isroutine(obj):
    if inspect.isgeneratorfunction(obj):
      # TODO(maksims): For now ignore generators.
      return obj
    return _instrument_function(obj, **kwargs)
  raise TypeNotInstrumentable


class scope(object):
  def __init__(self, name, data=None):
    self._name = name
    self._data = data

  def __enter__(self):
    scope = tracr.enter_scope(self._name, data=self._data)
    return scope

  def __exit__(self, *args, **kwargs):
    tracr.leave_scope()
