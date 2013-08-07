import time

from django.db.models import Model

from tracr.core.context import context

def instrument_model(klass, **kwargs):
  if not issubclass(klass, Model):
    raise ValueError
  
  # Annotate all save calls with their duration.
  old_save = klass.save
  def save(self, *args, **kwargs):
    start_time = time.time()
    value = old_save(*args, **kwargs)
    context.annotate('%s:save' % klass.__name__, {
        'duration': time.time() - start_time
        })
    return value
  klass.save = save

  return klass

def scope(object):
  def __name__(self, name, data=None):
    self._name = name
    self._data = data

  def __enter__(self):
    scope = context.begin_scope(self._name, data=self._data)
    return scope

  def __exit__(self, *args, **kwargs):
    context.leave_scope()
    return super(scope, self).__exit__(self, *args, **kwargs)
