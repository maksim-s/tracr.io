import unittest

from tracr.trace import exceptions, Trace


# TODO(usmanm): Add tests for serialization.
class TestDataStructure(unittest.TestCase):
  def test_basic(self):
    """ Tests all the basic data structure APIs. """
    trace = Trace(trace_id='trace_id', parent_scope_id='parent_id')
    trace.add_mark('mark1')
    scope1 = trace.create_scope('scope1')
    scope1.start()
    scope2 = scope1.add_child('scope2')
    self.assertEqual(scope2._parent, scope1)
    self.assertTrue(len(scope1._children) == 1)
    self.assertEqual(scope1._children[0], scope2)
    scope2.start()
    scope2.add_annotation('annotation2', data='lolcat2')
    self.assertTrue(len(scope2._annotations) == 1)
    scope2.end()
    scope1.add_annotation('annotation1', data='lolcat1')
    self.assertTrue(len(scope1._annotations) == 1)
    scope1.end()
    scope3 = trace.create_scope('scope3')
    scope3.start()
    scope3.end()
    self.assertTrue(len(trace._scopes) == 2)
    
  def test_invariant_violations(self):
    """ Tests failure cases when datastructure invariants are violated. """
    trace = Trace(trace_id='trace_id', parent_scope_id='parent_id')
    scope1 = trace.create_scope('scope1')
    self.assertRaises(exceptions.ScopeNotStarted, scope1.add_child, 'scope2')
    scope1.start()
    self.assertRaises(exceptions.ScopeAlreadyStarted, scope1.start)
    scope2 = scope1.add_child('scope2')
    self.assertRaises(exceptions.ScopeNotStarted, scope2.end)
    scope2.start()
    self.assertRaises(exceptions.UnclosedChildScopes, scope1.end)
