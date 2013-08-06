import time
import uuid

from tracr.utils.uuid import uuid1


class Serializable(object):
  def serialize(self):
    raise NotImplemented


from tracr.trace.scope import Scope


class Mark(Serializable):
  def __init__(self, name):
    self._name = name
    self._time = time.time()
    
  def serialize(self):
    return {
      'name': self._name,
      'time': self._time
      }


class Trace(Serializable):
  """
  `tracr.trace.base.Trace` is the top level object that monitors the request
  behavior.
  """
  class Type:
    ROOT = 0
    EXTENDED = 1 # Is this an extension of a remote trace?

  def __init__(self, trace_id=None, parent_scope_id=None):
    self._id = trace_id or uuid1()
    self._parent_scope_id = parent_scope_id
    self._type = (Trace.Type.EXTENDED if (trace_id and parent_scope_id)
                  else Trace.Type.ROOT)
    self._node_id = str(uuid.getnode())
    self._scopes = []
    self._marks = []

  def create_scope(self, name, data=None):
    scope = Scope(name, self, data=data)
    self._scopes.append(scope)
    return scope

  def add_mark(self, name):
    self._marks.append(Mark(name))

  def serialize(self):
    return {
      'tid': self._id,
      'parent_sid': self._parent_scope_id,
      'type': self._type,
      'node_id': self._node_id,
      'marks': [mark.serialize() for mark in self._marks],
      'scopes': [scope.serialize() for scope in self._scopes]
      }
