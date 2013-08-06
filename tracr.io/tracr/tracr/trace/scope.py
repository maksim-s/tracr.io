import time
import uuid

from functools import wraps

from tracr.trace.base import Serializable
from tracr.trace.exceptions import (ParentScopeNotStarted,
                                    ScopeAlreadyStarted,
                                    ScopeNotStarted,
                                    UnclosedChildScopes)


class Annotation(Serializable):
  """
  `tracr.trace.annotation.Annotation` is a top level class for any information
  that you want to store during a duration of a `tracr.trace.scope.Scope`.
  """
  def __init__(self, name, scope, data=None):
    """
    :param scope: `tracr.trace.scope.Scope` object
    :param data: python dictionary that contains all the data to be
    stored.
    """
    self._name = name
    self._scope = scope
    self._time = time.time()
    self._data = data

  def serialize(self):
    return {
      'name': self._name,
      'time': self._time,
      'data': self._data
      }


class Scope(Serializable):
  """
  `tracr.trace.scope.Scope` record all the information related to the timing in
  a `tracr.trace.base.Trace`.
  """
  def __init__(self, name, trace, data=None, parent=None):
    self._id = str(uuid.uuid4())
    self._name = name
    self._data = data or {}
    self._trace = trace
    self._parent = parent
    self._start_time = self._end_time = None
    self._children = []
    self._annotations = []

  def ensure_started(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
      if not self._start_time:
        raise ScopeNotStarted
      return method(self, *args, **kwargs)
    return wrapper

  def start(self):
    if self._start_time:
      raise ScopeAlreadyStarted
    if self._parent and not self._parent._start_time:
      raise ParentScopeNotStarted
    self._start_time = time.time()

  def update_data(self, key, value):
    self._data[key] = value

  @ensure_started
  def end(self):
    if not all(scope._end_time for scope in self._children):
      raise UnclosedChildScopes
    self._end_time = time.time()

  @ensure_started
  def add_child(self, name, data=None):
    scope = Scope(name, self._trace, parent=self, data=data)
    self._children.append(scope)
    return scope

  @ensure_started
  def add_annotation(self, name, data=None):
    self._annotations.append(Annotation(name, self, data=data))

  def serialize(self):
    return {
      'sid': self._id,
      'name': self._name,
      'start_time': self._start_time,
      'end_time': self._end_time,
      'data': self._data or None,
      'children': [scope.serialize() for scope in self._children],
      'annotations': [annotation.serialize()
                      for annotation in self._annotations]
      }
