import threading
import unittest

from testing_utils import DummyRequest
from tracr.core.context import current_thread_id, manager


class TestContextManager(unittest.TestCase):
  def test_context(self, extended_trace=False):
    request = DummyRequest()
    if extended_trace:
      request.set_tracr_header('tid', 'sid')
    context = manager.create_context(request)
    self.assertEqual(manager.get_context(), context)
    self.assertEqual(current_thread_id(), context.get_thread_id())

    scope1 = context.enter_scope('scope1')
    context.annotate('annotation1', data='hello world')
    context.mark('mark1')
    scope2 = context.enter_scope('scope2')
    context.annotate('annotation2')
    context.update_scope_data('hello', 'world')
    context.leave_scope()
    context.leave_scope()
    trace = context.get_trace()
    if extended_trace:
      self.assertEqual(trace._id, 'tid')
      self.assertEqual(trace._parent_scope_id, 'sid')
    else:
      self.assertTrue(trace._id is not None)
      self.assertEqual(trace._parent_scope_id, None)
    self.assertTrue(len(trace._scopes) == 1)
    self.assertTrue(trace._scopes[0] == scope1)
    self.assertEqual(scope1._name, 'scope1')
    self.assertTrue(len(scope1._children) == 1)
    self.assertTrue(scope1._children[0] == scope2)
    self.assertEqual(scope2._name, 'scope2')
    self.assertEqual(scope2._data['hello'], 'world')
    self.assertTrue(len(scope1._annotations) == 1)
    self.assertTrue(len(scope2._annotations) == 1)

    manager.destroy_context()

  def test_context_for_extended_trace(self):
    self.test_context(extended_trace=True)

  def test_multiple_threads(self):
    threads = []
    for i in xrange(10):
      threads.append(threading.Thread(target=self.test_context))
      threads.append(threading.Thread(target=
                                      self.test_context_for_extended_trace))
    for thread in threads:
      thread.start()
    for thread in threads:
      thread.join()
