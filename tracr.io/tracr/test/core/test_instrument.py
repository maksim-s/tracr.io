import unittest

from tracr import instrument, scope
from tracr.core.context import manager

from testing_utils import DummyRequest


class DummyClass(object):
  def dummy_method(self):
    return 'I am a dummy method.'

  def dummy_generator(self):
    yield 1

  def dummy_exception_function(self):
    raise Exception

def dummy_function():
  return 'Tracr.io is pretty chill.'


class TestFunctionInstrumentation(unittest.TestCase):
  def setUp(self):
    self.dummy_object = DummyClass()
    self.context = manager.create_context(DummyRequest())

  def test_regular_function(self):
    new_func = instrument(dummy_function)
    ret_value = new_func()
    trace = self.context.get_trace()
    last_scope = trace._scopes[-1]
    number_queries = last_scope._data['db_queries']['total_number']
    query_time = last_scope._data['db_queries']['total_time']
    self.assertEqual(ret_value, 'Tracr.io is pretty chill.')
    self.assertEqual(last_scope._name,
                     'dummy_function')
    self.assertEqual(number_queries, 0)
    self.assertEqual(query_time, 0)

  def test_method(self):
    new_func = instrument(self.dummy_object.dummy_method)
    ret_value = new_func()
    trace = self.context.get_trace()
    last_scope = trace._scopes[-1]
    self.assertEqual(ret_value, 'I am a dummy method.')
    self.assertEqual(last_scope._name,
                     'DummyClass:dummy_method')

  def test_generator_function(self):
    new_func = instrument(self.dummy_object.dummy_generator)
    self.assertEqual(new_func, self.dummy_object.dummy_generator)

  def test_exception(self):
    new_func = instrument(self.dummy_object.dummy_exception_function)
    try:
      new_func()
    except Exception:
      trace = self.context.get_trace()
      last_scope = trace._scopes[-1]
      self.assertEqual(last_scope._name,
          'DummyClass:dummy_exception_function')

  def test_block_scope(self):
    request = DummyRequest()
    context = manager.create_context(request)
    with scope('scope', data={'hello', 'world'}) as _scope:
      trace = context.get_trace()
      self.assertTrue(len(trace._scopes) == 1)
      self.assertEqual(_scope, trace._scopes[0])
    manager.destroy_context()
