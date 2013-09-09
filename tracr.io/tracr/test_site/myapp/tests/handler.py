from django.test import TestCase
from tracr.core.context import manager
from tracr.handlers.sql import record_sql

from myapp.models import ModelA
from myapp.tests import DummyRequest

def dummy_function():
  a = ModelA.objects.filter(id__lte=3)
  return a.count()


class SqlHandlerTestCase(TestCase):
  fixtures = ('modela.json', 'modelb.json')

  def setUp(self):
    self.context = manager.create_context(DummyRequest())

  def test_view_sql_handler(self):
    scope = self.context.enter_scope('scope')
    wrapped_dummy_function = record_sql(dummy_function)
    count = wrapped_dummy_function()
    self.assertTrue(len(scope._annotations) == 1)
