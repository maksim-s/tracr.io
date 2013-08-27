from django.core.cache import cache, get_cache
from django.core.cache.backends.base import BaseCache

import tracr

from tracr.handlers.base import Handler, Signal

# Signal that fires when cache functions are called.
cache_signal = Signal()


class CacheWrapper(BaseCache):
  def __init__(self, cache):
    self.cache = cache
  
  def __contains__(self, key):
    return self.cache.__contains__(key)

  def make_key(self, *args, **kwargs):
    return self.cache.make_key(*args, **kwargs)

  def validate_key(self, *args, **kwargs):
    self.cache.validate_key(*args, **kwargs)

  @cache_signal.dispatch
  def clear(self):
    return self.cache.clear()

  @cache_signal.dispatch
  def add(self, *args, **kwargs):
    return self.cache.add(*args, **kwargs)

  @cache_signal.dispatch
  def get(self, *args, **kwargs):
    return self.cache.get(*args, **kwargs)

  @cache_signal.dispatch
  def set(self, *args, **kwargs):
    return self.cache.set(*args, **kwargs)

  @cache_signal.dispatch
  def delete(self, *args, **kwargs):
    return self.cache.delete(*args, **kwargs)

  @cache_signal.dispatch
  def has_key(self, *args, **kwargs):
    return self.cache.has_key(*args, **kwargs)

  @cache_signal.dispatch
  def incr(self, *args, **kwargs):
    return self.cache.incr(*args, **kwargs)

  @cache_signal.dispatch
  def decr(self, *args, **kwargs):
    return self.cache.decr(*args, **kwargs)

  @cache_signal.dispatch
  def get_many(self, *args, **kwargs):
    return self.cache.get_many(*args, **kwargs)

  @cache_signal.dispatch
  def set_many(self, *args, **kwargs):
    self.cache.set_many(*args, **kwargs)

  @cache_signal.dispatch
  def delete_many(self, *args, **kwargs):
    self.cache.delete_many(*args, **kwargs)

  @cache_signal.dispatch
  def incr_version(self, *args, **kwargs):
    return self.cache.incr_version(*args, **kwargs)

  @cache_signal.dispatch
  def decr_version(self, *args, **kwargs):
    return self.cache.decr_version(*args, **kwargs)


def get_cache_wrapper(*args, **kwargs):
  return CacheWrapper(get_cache(*args, **kwargs))


class CacheHandler(Handler):
  def __init__(self):
    self._wrap_caches()
    cache_signal.connect(self._receiver)

  def _wrap_caches(self):
    global cache, get_cache
    # Wrap Django `default` cache and `get_cache` function.
    cache = CacheWrapper(cache)
    get_cache = get_cache_wrapper

  def _receiver(self, sender, *args, **kwargs):
    method_name = sender.__name__
    cache_key = kwargs['kwargs'].get('key', kwargs['args'][1])
    page_request = 'views.decorators.cache.cache_page' in cache_key
    header_request = 'views.decorators.cache.cache_header' in cache_key
    if method_name == 'get':
      if kwargs['value'] is None:
        tracr.annotate('CacheHandler:cache_miss',
                       data={'$duration': kwargs['duration'],
                             '$source': 'CacheHandler',
                             'page': page_request,
                             'header': header_request})
      else:
        tracr.annotate('CacheHandler:cache_hit',
                       data={'$duration': kwargs['duration'],
                             '$source': 'CacheHandler',
                             'page': page_request,
                             'header': header_request})
    elif method_name == 'get_many':
      hits = misses = 0
      for value in kwargs['value'].itervalues():
        if value is None:
          misses += 1
        else:
          hits += 1
      if misses:
        tracr.annotate('CacheHandler:cache_miss',
                       data={'$duration': kwargs['duration'],
                             '$source': 'CacheHandler',
                             'items': misses})
      if hits:
        tracr.annotate('CacheHandler:cache_hit',
                       data={'$duration': kwargs['duration'],
                             '$source': 'CacheHandler',
                             'items': hits})
    data = {'$duration': kwargs['duration'],
            '$module': sender.__module__,
            '$source': 'CacheHandler'}
    if kwargs['exception']:
      data['$exception'] = str(kwargs['exception'])
    tracr.annotate('%s:%s' % (sender.__class__.__name__, sender.__name__),
                   data=data)

  def process_request(self, request):
    pass

  def process_view(self, request, view_func, view_args, view_kwargs):
    pass

  def process_template_response(self, request, response):
    pass

  def process_response(self, request, response):
    pass

  def process_exception(self, request, exception):
    pass

