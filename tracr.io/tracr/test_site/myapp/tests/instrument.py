from django.test import TestCase
from tracr import instrument
from tracr.core.context import manager

from myapp.models import ModelA
from myapp.tests import DummyRequest


class InstrumentTestCase(TestCase):
  fixtures = ('modela.json', 'modelb.json')

  def setUp(self):
    self.context = manager.create_context(DummyRequest())
    instrument(ModelA)

  def test_instrument_model(self):
    scope = self.context.enter_scope('scope')
    a = ModelA.objects.order_by('?')[0]
    a.save()
    self.assertTrue(len(scope._annotations) == 1)
    self.assertEqual(scope._annotations[-1]._name, 'ModelA:save')
    a.foreign
    self.assertTrue(len(scope._annotations) == 2)
    self.assertTrue(scope._annotations[-1]._name in
        ('ModelA:foreign:get_queryset', 'ModelA:foreign:get_query_set'))
    a.o2o
    self.assertTrue(len(scope._annotations) == 3)
    self.assertTrue(scope._annotations[-1]._name in
        ('ModelA:o2o:get_queryset', 'ModelA:o2o:get_query_set'))
    a.o2m.all()
    self.assertTrue(len(scope._annotations) == 4)
    self.assertTrue(scope._annotations[-1]._name in
        ('ModelA:o2m:get_queryset', 'ModelA:o2m:get_query_set'))
    a.m2m.all()
    self.assertTrue(len(scope._annotations) == 5)
    self.assertTrue(scope._annotations[-1]._name in
        ('ModelA:m2m:get_queryset', 'ModelA:m2m:get_query_set'))
    self.context.leave_scope()

    # Test with prefetch/select related.
    scope = self.context.enter_scope('scope')
    a = (ModelA.objects
         .select_related('foreign', 'o2o')
         .prefetch_related('o2m', 'm2m')).order_by('?')[0]
    self.assertTrue(len(scope._annotations) == 4)
    self.assertTrue({annotation._name for annotation in scope._annotations} in
                     ({'ModelA:o2m:get_prefetch_queryset',
                       'ModelA:o2m:get_queryset',
                       'ModelA:m2m:get_prefetch_queryset',
                       'ModelA:m2m:get_queryset'},
                      {'ModelA:o2m:get_prefetch_query_set',
                       'ModelA:o2m:get_query_set',
                       'ModelA:m2m:get_prefetch_query_set',
                       'ModelA:m2m:get_query_set'}))
    a.foreign
    a.o2o
    self.assertTrue(len(scope._annotations) == 4)

