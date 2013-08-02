#!/usr/bin/env python
import os
import sys

def add_to_sys_path(rel_path):
  """ Adds a directory to the system python path. """
  return sys.path.append(os.path.abspath(
      os.path.join(os.path.dirname(__file__), rel_path)) + '/')

add_to_sys_path('.')
add_to_sys_path('..')

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
