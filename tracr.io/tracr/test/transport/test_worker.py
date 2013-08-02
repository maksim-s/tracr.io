import threading
import time
import unittest

from functools import wraps

from tracr.transport import worker


class TestSyncWorker(unittest.TestCase):
  def setUp(self):
    self.worker = worker.SyncWorker()
    self.task_sleep_time = 0

  def test_execute(self):
    """ Tests Worker.execute(...) """
    def task(array):
      array.append(1)
    array = []
    self.worker.execute(task, args=[array])
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

  def test_success_callback(self):
    """ Tests Worker.execute(...) with success callback. """
    def task(success_cb=None):
      return 1
    array = []
    def success_cb(data):
      array.append(data)
    self.worker.execute(task, success_cb=success_cb)
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

  def test_failure_callback(self):
    """ Tests Worker.execute(...) with failure callback. """
    def task(failure_cb=None):
      raise Exception(1)
    array = []
    def failure_cb(exception):
      array.append(exception.message)
    self.worker.execute(task, failure_cb=failure_cb)
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)


class TestAsyncWorker(unittest.TestCase):
  HOSTS = ('http://tracr.io', 'gevent+http://tracr.io/')

  def run_for_all_hosts(method):
    @wraps(method)
    def wrapper(self):
      for host in TestAsyncWorker.HOSTS:
        self.host = host
        method(self, self.host_to_worker[host])
        self.host = None
    return wrapper

  def setUp(self):
    self.host_to_worker = {}
    for host in TestAsyncWorker.HOSTS:
      self.host_to_worker[host] = (
          worker.AsyncWorker(host=host, queue_size=2, shutdown_timeout=0))
    self.task_sleep_time = 0.2

  def tearDown(self):
    for worker in self.host_to_worker.itervalues():
      worker._kill()

  def set_worker_config(self, queue_size, shutdown_timeout):
    self.host_to_worker[self.host]._kill()
    self.host_to_worker[self.host] = (
      worker.AsyncWorker(host=self.host, queue_size=queue_size,
                         shutdown_timeout=shutdown_timeout))
    return self.host_to_worker[self.host]

  @run_for_all_hosts
  def test_execute(self, worker):
    """ Tests Worker.execute(...) """
    def task(array):
      array.append(1)
    array = []
    worker.execute(task, args=[array])
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

  @run_for_all_hosts
  def test_success_callback(self, worker):
    """ Tests Worker.execute(...) with success callback. """
    def task(success_cb=None):
      return 1
    array = []
    def success_cb(data):
      array.append(data)
    worker.execute(task, success_cb=success_cb)
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

  @run_for_all_hosts
  def test_failure_callback(self, worker):
    """ Tests Worker.execute(...) with failure callback. """
    def task(failure_cb=None):
      raise Exception(1)
    array = []
    def failure_cb(exception):
      array.append(exception.message)
    worker.execute(task, failure_cb=failure_cb)
    time.sleep(self.task_sleep_time) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

  @run_for_all_hosts
  def test_queue_limit(self, worker):
    """ Tests that task queue limit works. """
    def task(array, item, wait_time=0):
      if wait_time:
        time.sleep(wait_time)
      array.append(item)
    array = []
    # Spawn first task to block async worker.
    worker.execute(task, args=[array, 0], kwargs={'wait_time': 1})
    # We should only execute at most 1 of these.
    for i in xrange(1, 2):
      worker.execute(task, args=[array, i])
    time.sleep(2)
    self.assertTrue(len(array) == 2)
    self.assertTrue(all(x in (0, 1)  for x in array))
    
  @run_for_all_hosts
  def test_shutdown_timeout(self, worker):
    """ Tests that async worker is still in the right timeout. """
    def task(array):
      time.sleep(0.01)
      array.append(1)
    worker = self.set_worker_config(1000, 5) # Shutdown timeout 5s.
    array = []
    for i in xrange(20):
      worker.execute(task, args=[array])
    self.assertTrue(worker._thread and
                    worker._thread.is_alive() and
                    worker._queue.qsize() > 0)
    # Kill in a separate thread which will block for `shutdown_timeout`
    # seconds before freeing `worker._task_thread`.
    kill_thread = threading.Thread(target=worker._kill)
    kill_thread.start()
    self.assertTrue(worker._thread and
                    worker._thread.is_alive() and
                    worker._queue.qsize() > 0)
    self.assertTrue(len(array) < 20)
    time.sleep(2) # Kill thread should be done in 2ish seconds.
    # Ensure that kill thead is no longer alive (proxy for interpreter is
    # shut down), `worker._task_thread` is freed and all tasks were 
    # completed successfully.
    self.assertTrue(not worker._thread and
                    not kill_thread.is_alive() and
                    len(array) == 20)
