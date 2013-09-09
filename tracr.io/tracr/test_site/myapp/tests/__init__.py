import json

from tracr.conf import constants

class DummyRequest(object):
  def __init__(self):
    self.META = {}

  def set_tracr_header(self, trace_id, scope_id):
    self.META[constants.HTTP_HEADER] = json.dumps({'tid': trace_id,
                                                   'sid': scope_id})

# Import all test cases here.
from myapp.tests.instrument import InstrumentTestCase
from myapp.tests.handler import SqlHandlerTestCase
