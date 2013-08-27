from __future__ import absolute_import

import inspect
import os
import re
import sys

import django

_DJANGO_PATH = os.path.realpath(os.path.dirname(django.__file__))
_PYTHON_NATIVE_LIB_RE = re.compile('lib/python\d\.\d/(?!site\-packages/)')

class FrameInfo(object):
  def __init__(self, frame):
    self.frame = frame
    self.line_num = frame.f_lineno
    self.function_name = frame.f_code.co_name
    self.file_path = os.path.realpath(inspect.getsourcefile(frame) or
                                      inspect.getfile(frame))
  
  def __repr__(self):
    return '%s [%s:%s]' % (self.function_name, self.file_path, self.line_num)


def get_stack(depth=None, include_django=True):
  frame = sys._getframe(1) # Don't fetch frame for `get_stack`
  frames = []
  while frame:
    frame_info = FrameInfo(frame)
    frame = frame.f_back
    if _PYTHON_NATIVE_LIB_RE.search(frame_info.file_path):
      # Ignore frames for all Python native libraries.
      continue
    if not include_django and frame_info.file_path.startswith(_DJANGO_PATH):
      # Ignore frames for Django functions.
      continue
    frames.append(frame_info)
    if len(frames) == depth:
      break
  return frames
