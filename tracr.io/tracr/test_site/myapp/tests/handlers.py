from django.db import connection
from django.test import TestCase

from tracr.core.context import manager
from tracr.handlers.sql import record_sql

from myapp.models import ModelA
from myapp.tests import DummyRequest

def dummy_function():
  a = ModelA.objects.filter(id__lte=3)
  b = ModelA.objects.filter(id__gt=5)
  return a.count() + b.count()


class SqlHandlerTestCase(TestCase):
  fixtures = ('modela.json', 'modelb.json')

  def setUp(self):
    global connection
    connection.use_debug_cursor = True
    self.context = manager.create_context(DummyRequest())

  def test_view_sql_handler(self):
    scope = self.context.enter_scope('scope')
    wrapped_dummy_function = record_sql(dummy_function)
    count = wrapped_dummy_function()
    self.assertTrue(len(scope._annotations) == 1)
    self.assertEqual(scope._annotations[-1]._name, 'dummy_function')
    self.assertEqual(scope._annotations[-1]._data['total_number'], 2)

