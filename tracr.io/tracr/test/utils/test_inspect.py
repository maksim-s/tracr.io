import unittest
import os

from tracr.utils.inspect import get_stack

FILE_PATH = os.path.realpath(__file__).rstrip('c')

class TestInspectUtils(unittest.TestCase):
  def test_get_trace(self):
    stack = get_stack() # This should be the line number.
    frame = stack[0]
    self.assertEqual(frame.function_name, 'test_get_trace')
    self.assertEqual(frame.file_path.rstrip('c'), FILE_PATH)
    self.assertEqual(frame.line_num, 10)

    def function1():
      stack = get_stack() # This should be the first line number.
      frame = stack[0]
      self.assertEqual(frame.function_name, 'function1')
      self.assertEqual(frame.file_path.rstrip('c'), FILE_PATH)
      self.assertEqual(frame.line_num, 17)
      frame = stack[1]
      self.assertEqual(frame.function_name, 'test_get_trace')
      self.assertEqual(frame.file_path.rstrip('c'), FILE_PATH)
      self.assertEqual(frame.line_num, 26)
    function1() # This should be the second line number.
