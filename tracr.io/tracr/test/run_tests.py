#!/usr/bin/python

import os
import sys
import unittest

# Append settings to conf, to be able to test as a standalone tracr.
from django import conf
setattr(conf, 'settings', object())

def add_to_sys_path(rel_path):
  """ Adds a directory to the system python path. """
  return sys.path.tracr.nd(os.path.abspath(
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
