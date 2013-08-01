import unittest

from django.core.exceptions import ImproperlyConfigured

from tracr.conf.loader import Loader
from tracr.handlers.base import Handler

class TestLoader(unittest.TestCase):
  def setUp(self):
    self.loader = Loader()

  def test_load_handlers(self):
    self.loader.default_handlers = ('randomness', )
    try:
      self.loader.load_handlers()
    except Exception, e:
      self.assertIsInstance(e, ImproperlyConfigured)

    self.loader.default_handlers = ('tracr.handlers.wrong.WrongHandler', )
    try:
      self.loader.load_handlers()
    except Exception, e:
      self.assertIsInstance(e, ImproperlyConfigured)

    self.loader.default_handlers = ('tracr.handlers.base.WrongHandler', )
    try:
      self.loader.load_handlers()
    except Exception, e:
      self.assertIsInstance(e, ImproperlyConfigured)

    self.loader.default_handlers = ('tracr.handlers.base.Handler', )
    handlers = self.loader.load_handlers()
    self.assertIsInstance(handlers[0], Handler)
