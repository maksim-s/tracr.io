import unittest

from tracr.core.context import manager
from tracr.core.instrument import scope


class DummyRequest(object):
  def __init__(self):
    self.META = {}

class TestInstrumentFunctions(unittest.TestCase):
  def test_block_scope(self):
    request = DummyRequest()
    context = manager.create_context(request)
    with scope('scope', data={'hello', 'world'}) as _scope:
      trace = context.get_trace()
      self.assertTrue(len(trace._scopes) == 1)
      self.assertEqual(_scope, trace._scopes[0])
    manager.destroy_context()
