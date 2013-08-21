import os
import sys
import unittest

# Configure Django settings.
from django.conf import settings; settings.configure()

def add_to_sys_path(rel_path):
  """ Adds a directory to the system python path. """
  return sys.path.append(os.path.abspath(
      os.path.join(os.path.dirname(__file__), rel_path)) + '/')

add_to_sys_path('.')
add_to_sys_path('..')

if __name__ == '__main__':
  # Load all tests.
  test_suites = unittest.defaultTestLoader.discover(
      start_dir=os.path.dirname(__file__))
  runner = unittest.TextTestRunner()
  for test_suite in test_suites:
    runner.run(test_suite)
