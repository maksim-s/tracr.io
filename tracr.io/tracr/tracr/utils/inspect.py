import inspect
import os
import sys

import django

DJANGO_PATH = os.path.realpath(os.path.dirname(django.__file__))


class FrameInfo(object):
  def __init__(self, frame):
    self.frame = frame
    self.line_num = frame.f_lineno
    self.function_name = frame.f_code.co_name
    self.file_path = os.path.realpath(inspect.getsourcefile(frame) or
                                      inspect.getfile(frame))


def get_stack(depth=None, include_django=True):
  frame = sys._getframe(1) # Don't fetch frame for `get_stack`
  frames = []
  frame_num = 0
  while frame:
    frame_info = FrameInfo(frame)
    if not include_django:
      # Ignore frames for Django functions.
      if frame_info.file_path.startswith(DJANGO_PATH):
        continue
    if depth is not None and frame_num >= depth:
      break
    frames.append(frame_info)
    frame = frame.f_back
    frame_num += 1
  return frames
