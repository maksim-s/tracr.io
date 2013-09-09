import unittest

from tracr.handlers.base import Handler
from tracr.core.middleware import TracrMiddleware

from testing_utils import DummyRequest

class TestMiddleware(unittest.TestCase):
  def setUp(self):
    middleware = TracrMiddleware()
    handler_a = DummyHandlerA()
    handler_b = DummyHandlerB()
    middleware.handlers = (handler_a, handler_b)
    self.middleware = middleware
    self.request = DummyRequest()

  def test_process_request(self):
    self.middleware.process_request(self.request)
    self.assertEqual(self.request.META['a'], 1)
    self.assertEqual(self.request.META['b'], 1)


  def test_process_view(self):
    self.middleware.process_view(self.request, None, None, None)
    self.assertEqual(self.request.META['a'], 1)
    self.assertEqual(self.request.META['b'], 1)

  def test_process_template_response(self):
    response = {}
    self.middleware.process_template_response(self.request, response)
    self.assertEqual(response['a'], 1)
    self.assertEqual(response['b'], 1)

  def test_process_response(self):
    response = {}
    self.middleware.process_response(self.request, response)
    self.assertEqual(response['a'], 1)
    self.assertEqual(response['b'], 1)

  def process_exception(self):
    self.middleware.process_exception(self.request, None)
    self.assertEqual(self.request.META['a'], 1)
    self.assertEqual(self.request.META['b'], 1)

class DummyHandlerA(Handler):
  def process_request(self, request):
    request.META['a'] = 1

  def process_view(self, request, view_func, view_args, view_kwargs):
    request.META['a'] = 1

  def process_template_response(self, request, response):
    response['a'] = 1

  def process_response(self, request, response):
    response['a'] = 1

  def process_exception(self, request, exception):
    request.META['a'] = 1


class DummyHandlerB(Handler):
  def process_request(self, request):
    request.META['b'] = 1

  def process_view(self, request, view_func, view_args, view_kwargs):
    request.META['b'] = 1

  def process_template_response(self, request, response):
    response['b'] = 1

  def process_response(self, request, response):
    response['b'] = 1

  def process_exception(self, request, exception):
    request.META['b'] = 1
