import threading
import time
import unittest

from app.client import worker

class TestSyncWorker(unittest.TestCase):
  def setUp(self):
    self.worker = worker.SyncWorker()

  def test_execute(self):
    """ Tests Worker.execute(...) """
    def task(array):
      array.append(1)
    array = []
    self.worker.execute(task, array)
    time.sleep(1) # Wait for task to complete.
    self.assertTrue(len(array) == 1)
    self.assertTrue(array[0] == 1)

class TestAsyncWorker(TestSyncWorker):
  def setUp(self):
    self.worker = worker.AsyncWorker(queue_size=2, shutdown_timeout=0)

  def tearDown(self):
    self.worker._kill()

  def set_worker_config(self, queue_size, shutdown_timeout):
    self.worker._kill()
    self.worker = worker.AsyncWorker(queue_size=queue_size,
                                     shutdown_timeout=shutdown_timeout)

  def test_queue_limit(self):
    """ Tests that task queue limit works. """
    def task(array, item, wait_time=0):
      if wait_time:
        time.sleep(wait_time)
      array.append(item)
    array = []
    # Spawn first task to block async worker.
    self.worker.execute(task, array, 0, wait_time=1)
    # We should only execute at most 1 of these.
    for i in xrange(1, 2):
      self.worker.execute(task, array, i)
    time.sleep(2)
    self.assertTrue(len(array) == 2)
    self.assertTrue(all(x in (0, 1)  for x in array))
    
  def test_shutdown_timeout(self):
    """ Tests that async worker is still in the right timeout. """
    def task(array):
      time.sleep(0.01)
      array.append(1)
    self.set_worker_config(1000, 5) # Shutdown timeout 5s.
    array = []
    for i in xrange(20):
      self.worker.execute(task, array)
    self.assertTrue(self.worker._task_thread and
                    self.worker._task_thread.is_alive() and
                    self.worker._queue.qsize() > 0)
    # Kill in a separate thread which will block for `shutdown_timeout`
    # seconds before freeing `self.worker._task_thread`.
    kill_thread = threading.Thread(target=self.worker._kill)
    kill_thread.start()
    self.assertTrue(self.worker._task_thread and
                    self.worker._task_thread.is_alive() and
                    self.worker._queue.qsize() > 0)
    self.assertTrue(len(array) < 20)
    time.sleep(2) # Kill thread should be done in 2ish seconds.
    # Ensure that kill thead is no longer alive (proxy for interpreter is
    # shut down), `self.worker._task_thread` is freed and all tasks were 
    # completed successfully.
    self.assertTrue(not self.worker._task_thread and
                    not kill_thread.is_alive() and
                    len(array) == 20)
