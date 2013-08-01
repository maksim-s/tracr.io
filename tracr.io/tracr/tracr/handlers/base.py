class Handler(object):
  def __init__(self, *args, **kwargs):
    pass

  def process_request(self, request):
    pass

  def process_view(self, request, view_func, view_args, view_kwargs):
    pass

  def process_template_response(self, request, response):
    pass

  def process_response(self, request, response):
    pass

  def process_exception(self, request, exception):
    pass
