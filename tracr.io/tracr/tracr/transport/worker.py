import atexit
import logging
import Queue
import threading
import urlparse

from django.core.exceptions import ImproperlyConfigured

from tracr.conf import defaults

log = logging.getLogger(__name__)


class Worker(object):
  """ Interface for a worker that any instance of 
  `tracr.client.transport.Transport` can use to execute tasks (e.g. sending
  a trace to ther server). """
  def __init__(self, *args, **kwargs):
    pass

  def execute(self, function, args=[], kwargs={}, success_cb=None,
              failure_cb=None):
   raise NotImplemented


class SyncWorker(Worker):
  """ Executes all task synchronously. """
  def execute(self, function, args=[], kwargs={}, success_cb=None,
              failure_cb=None):
    try:
      result = function(*args, **kwargs)
      if callable(success_cb):
        success_cb(result)
    except Exception as e:
      if callable(failure_cb):
        failure_cb(e)


class AsyncWorker(Worker):
  """ Executes all tasks in a separate daemon thread. """

  class Thread(object):
    """ Wrapper class for different concurrency models. """
    def __init__(self, host=defaults.HOST, target=None):
      # Add all supported *protocols* to urlparse.
      for attr in (s for s in dir(urlparse) if s.startswith('uses_')):
        uses = set(getattr(urlparse, attr)) | {'gevent+http',
                                               'gevent+https'}
        setattr(urlparse, attr, list(uses))

      scheme = urlparse.urlparse(host).scheme
      if scheme in ('http', 'https'):
        # TODO(usmanm): Think of a more apt name. Fiber doesn't make sense but
        # I didn't wanna use thread here.
        self._fiber = threading.Thread(target=target)
        # Make daemon so it doesn't block the application from terminating.
        self._fiber.setDaemon(True)
      elif scheme in ('gevent+http', 'gevent+https'):
        try:
          import gevent
        except ImportError:
          # TODO(usmanm): Add proper exception here.
          raise Exception
        self._fiber = gevent.Greenlet.spawn(target)
        self._fiber.is_alive = lambda x: x.dead == True
      else:
        raise ImproperlyConfigured

    def start(self):
      self._fiber.start()

    def is_alive(self):
      return self._fiber.is_alive()

    def join(self, timeout):
      if hasattr(self._fiber, 'kill'):
        self._fiber.kill(timeout=timeout)
      else:
        self._fiber.join(timeout)

  kill_signal = object()
  kill_task = (kill_signal, None, None, None, None)

  def __init__(self, queue_size=defaults.QUEUE_SIZE, 
               shutdown_timeout=defaults.SHUTDOWN_TIMEOUT, *args, **kwargs):
    self._queue = Queue.Queue(maxsize=queue_size)
    self._shutdown_timeout = (shutdown_timeout if shutdown_timeout >= 0
                              else None)

    # Set up task thread.
    self._thread = AsyncWorker.Thread(target=self._run)
    self._thread.start()
    atexit.register(self._kill)

  def _kill(self):
    if not (self._shutdown_timeout and
            self._queue.qsize() and
            self._thread and
            self._thread.is_alive()):
      return
    log.info('AsyncWorker is flushing queued requests; '
             'will terminate in %s seconds.' % self._shutdown_timeout)
    try:
      # Try to queue up `AsyncWorker.kill_signal` and gracefully kill
      # the daemon thread.
      self._queue.put_nowait(AsyncWorker.kill_task)
    except Queue.Full:
      # Just try waiting for `self._shutdown_time` now.
      pass
    self._thread.join(self._shutdown_timeout)
    self._thread = None

  def _run(self):
    while True:
      function, args, kwargs, success_cb, failure_cb = self._queue.get()
      if function == AsyncWorker.kill_signal:
        self._queue.task_done()
        return
      try:
        result = function(*args, **kwargs)
        if callable(success_cb):
          success_cb(result)
      except Exception as e:
        if callable(failure_cb):
          failure_cb(e)
      self._queue.task_done()

  def execute(self, function, args=[], kwargs={}, success_cb=None,
              failure_cb=None):
    try:
      self._queue.put_nowait((function, args, kwargs, success_cb, failure_cb))
    except Queue.Full:
      log.error('AsyncWorker task queue is full!')
