import unittest

from app.handlers.base import Handler
from app.middleware import Middleware

class TestMiddleware(unittest.TestCase):
  def setUp(self):
    middleware = Middleware()
    handler_a = DummyHandlerA()
    handler_b = DummyHandlerB()
    middleware.handlers = (handler_a, handler_b)
    self.middleware = middleware

  def test_process_request(self):
    request = {}
    self.middleware.process_request(request)
    self.assertEqual(request['a'], 1)
    self.assertEqual(request['b'], 1)


  def test_process_view(self):
    request = {}
    self.middleware.process_view(request, None, None, None)
    self.assertEqual(request['a'], 1)
    self.assertEqual(request['b'], 1)

  def test_process_template_response(self):
    request = {}
    response = {}
    self.middleware.process_template_response(request, response)
    self.assertEqual(response['a'], 1)
    self.assertEqual(response['b'], 1)

  def test_process_response(self):
    request = {}
    response = {}
    self.middleware.process_response(request, response)
    self.assertEqual(response['a'], 1)
    self.assertEqual(response['b'], 1)

  def process_exception(self):
    request = {}
    self.middleware.process_exception(request, None)
    self.assertEqual(request['a'], 1)
    self.assertEqual(request['b'], 1)

class DummyHandlerA(Handler):
  def process_request(self, request):
    request['a'] = 1

  def process_view(self, request, view_func, view_args, view_kwargs):
    request['a'] = 1

  def process_template_response(self, request, response):
    response['a'] = 1
    return response

  def process_response(self, request, response):
    response['a'] = 1
    return response

  def process_exception(self, request, exception):
    request['a'] = 1


class DummyHandlerB(Handler):
  def process_request(self, request):
    request['b'] = 1

  def process_view(self, request, view_func, view_args, view_kwargs):
    request['b'] = 1

  def process_template_response(self, request, response):
    response['b'] = 1
    return None

  def process_response(self, request, response):
    response['b'] = 1
    return None

  def process_exception(self, request, exception):
    request['b'] = 1
