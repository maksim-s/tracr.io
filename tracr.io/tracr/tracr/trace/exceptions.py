class ParentScopeNotStarted(Exception):
  pass


class ScopeNotStarted(Exception):
  pass


class ScopeAlreadyStarted(Exception):
  pass


class UnclosedChildScopes(Exception):
  pass
