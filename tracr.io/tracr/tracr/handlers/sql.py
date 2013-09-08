from functools import wraps

from django.conf import settings
from django.db import connection

from handlers.base import Handler

import tracr

def record_sql(func):
  """
  Decorator that creates annotations for the decorated function
  with all the SQL information.
  """
  @wraps(func)
  def new_func(*args, **kwargs):
    function_name = func.__name__
    data = {'$module': func.__module__}
    scope_name = function_name
    if hasattr(func, 'im_class'):
      # The function is a method of some class.
      class_name = func.im_class.__name__
      scope_name = '%s:%s' % (class_name, function_name)
    exception = None
    start_queries = set(connection.queries)
    try:
      value = func(*args, **kwargs)
    except Exception as e:
      tracr.annotate(scope_name, {
        '$exception': str(e),
        '$source': 'SqlHandler'})
      exception = e
    end_queries = set(connection.queries)
    function_queries = end_queries - start_queries
    queries_time = sum(query['time'] for query in function_queries)
    query_data = {
        '$source': 'SqlHandler',
        'total_number': len(function_queries),
        'total_time': queries_time
        }
    tracr.annotate(scope_name, query_data)
    if exception:
      raise exception
    return value
  return new_func

class SqlHandler(Handler):
  # TODO(maksims): not sure what to do when a connection can be shared.
  # For now ignoring this handler if connection.allow_thread_sharing
  def __init__(self, *args, **kwargs):
    self._use_debug_cursor()

  def _use_debug_cursor(self):
    """
    Make sure that the debug cursor is used, so that the queries are logged.
    """
    global connection
    connection.use_debug_cursor = True

  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    Record the sql queries, the number of queries, the duration of every query,
    and the total time spent querying.
    """
    if not connection.allow_thread_sharing:
      view_func = record_sql(view_func)

  def process_template_response(self, request, response):
    """
    Record the same information as in process_view, to monitor DB accesses
    during template rendering.
    """
    if hasattr(response, 'render') and not connection.allow_thread_sharing:
      response.render = record_sql(response.render)
    return response

