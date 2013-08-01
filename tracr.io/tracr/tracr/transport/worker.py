import logging
import Queue
import threading

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
  kill_signal = object()
  kill_task = (kill_signal, None, None, None, None)

  def __init__(self, queue_size=defaults.QUEUE_SIZE, 
               shutdown_timeout=defaults.SHUTDOWN_TIMEOUT, *args, **kwargs):
    self._queue = Queue.Queue(maxsize=queue_size)
    self._shutdown_timeout = shutdown_timeout

    # Set up task thread.
    self._task_thread = threading.Thread(target=self._run)
    # Make daemon so it doesn't block the application from terminating.
    self._task_thread.setDaemon(True)
    self._task_thread.start()

  def _kill(self):
    if not (self._shutdown_timeout and
            self._task_thread and
            self._task_thread.is_alive() and
            self._queue.qsize()):
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
    timeout = self._shutdown_timeout if self._shutdown_timeout >= 0 else None
    self._task_thread.join(timeout)
    self._task_thread = None

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
