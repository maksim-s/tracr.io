from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from tracr.conf import defaults


class Loader(object):

  def __init__(self):
    pass

  def load_handlers(self):
    handlers = []
    handler_paths = getattr(settings,
                            'TRACR_HANDLERS',
                            defaults.TRACR_HANDLERS)
    for handler_path in handler_paths:
      try:
        separator = handler_path.rindex('.')
      except ValueError:
        raise ImproperlyConfigured(
            '%s is not a proper handler path.' % handler_path)
      handler_module, handler_name = (handler_path[:separator],
                                      handler_path[separator + 1:])
      try:
        module = import_module(handler_module)
      except ImportError:
        raise ImproperlyConfigured(
            "Couldn't import %s." % handler_module)

      try:
        handler_class = getattr(module, handler_name)
      except AttributeError:
        raise ImproperlyConfigured(
            '%s.%s is not a valid handler.' % (handler_module, handler_name))

      # TODO(maksims): we can pass settings to handlers from here.
      handler = handler_class()
      handlers.append(handler)
    return handlers

