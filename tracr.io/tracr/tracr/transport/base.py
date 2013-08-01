import requests
import types
import zlib

from tracr.transport import worker
from tracr.conf import defaults


class Transport(object):
  def __init__(self, host=defaults.HOST, async=defaults.ASYNC_WORKER,
               *args, **kwargs):
    self._host = host
    if async:
      self._worker = worker.AsyncWorker(*args, **kwargs)
    else:
      self._worker = worker.SyncWorker(*args, **kwargs)

    # Wrap each send_* method with spawn_worker_task to submit all send 
    # requests to the worker.
    for attr in dir(self):
      attr_value = getattr(self, attr)
      if not (isinstance(attr_value, types.FunctionType) and
              attr_value.func_name.startswith('send_')):
        continue
      setattr(self, attr, self.spawn_worker_task(attr_value))

  def spawn_worker_task(self, method):
    def wrapper(self, *args, **kwargs):
      self._worker.execute(method, *args, **kwargs)

  def send_trace(self, trace):
    raise NotImplemented


class HttpTransport(Transport):
  def send_trace(self, trace):
    data = zlib.compress(trace.serialize())
    # TODO(usmanm): Make request to the correct endpoint.
    response = requests.post(self._host, data=data)
    assert response.status_code == requests.codes.ok
    # TODO(usmanm): Validate response.
