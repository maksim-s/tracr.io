import sys

from tracr.core.context import context
from tracr.core.instrument import instrument, scope

__all__ = ('annotate', 'enter_scope', 'instrument', 'leave_scope', 'mark', 
           'scope', 'update_scope_data')

# Proxy methods of `ActiveContext` to `tracr` module.
for attr in ('enter_scope', 'leave_scope', 'annotate', 'mark', 
             'update_scope_data'):
  setattr(sys.modules[__name__], attr, getattr(context, attr))
