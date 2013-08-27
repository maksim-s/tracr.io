from functools import wraps

from django.db import connection

from handlers.base import Handler

def record_sql(func):
  @wraps(func)
  def new_func(*args, **kwargs):
    value = func(*args, **kwargs)
    return value
  return new_func

class SqlHandler(Handler):
  def __init__(self, *args, **kwargs):
    pass

  def process_view(self, request, view_func, view_args, view_kwargs):
    """
    Record the sql queries, the number of queries, the duration of every query,
    and the total time spent querying.
    """
    view_func = record_sql(view_func)

  def process_template_response(self, request, response):
    """
    Record the same information as in process_view, to monitor DB accesses
    during template rendering.
    """
    if hasattr(response, 'render'):
      response.render = record_sql(response.render)
    return response

