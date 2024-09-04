from django.core.cache import cache
import json

class CacheMethods:
    def getCache(key):
        return cache.get(key)

    def setCache(key, value, timeout):
        cache.set(key, json.dumps(value,ensure_ascii=False), timeout)

    def deleteCache(key):
        cache.delete(key)

    def cacheIsExist(key):
        approximateCache = cache.get(key)

        if approximateCache:
            return True
        
        return False