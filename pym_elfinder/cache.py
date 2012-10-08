# -*- coding_ utf-8 -*-

class Cache(object):
    def __init__(self, cache_dict):
        """Implements a simple cache in the session

        ``cache_dict`` must be an object that implements the dict interface
        and stores the items persistently between requests. E.g. Pyramid's
        ``request.session`` can be used here.
        """
        self._cache_dict = cache_dict

    def get(self, k, default=None):
        try:
            return self._cache_dict[k]
        except KeyError:
            if default is not None:
                return default
            else:
                raise

    def set(self, k, v):
        self._cache_dict[k] = v

    def delete(self, k):
        del self._cache_dict[k]
