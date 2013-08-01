from tracr.conf.loader import Loader

class Middleware(object):
  """
  Main middleware that combines all handlers together.
  """

  def __init__(self):
    self.loader = Loader()
    self.handlers = self.loader.load_handlers()

  def process_request(self, request):
    for handler in self.handlers:
      handler.process_request(request)

  def process_view(self, request, view_func, view_args, view_kwargs):
    for handler in self.handlers:
      handler.process_view(request,
                           view_func,
                           view_args,
                           view_kwargs)

  def process_template_response(self, request, response):
    for handler in self.handlers:
      handler_response = handler.process_template_response(request, response)
      if handler_response:
        response = handler_response
    return response

  def process_response(self, request, response):
    for handler in self.handlers:
      handler_response = handler.process_response(request, response)
      if handler_response:
        response = handler_response
    return response

  def process_exception(self, request, exception):
    for handler in self.handlers:
      handler.process_request(request)

