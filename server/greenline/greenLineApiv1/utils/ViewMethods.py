from rest_framework import status
import json

from .CacheMethods import CacheMethods        

class ViewMethods():
    def __init__(self):
        pass

    def getMethod(methodData,timeOut):
        approximateCacheData = CacheMethods.getCache(methodData.cacheName)

        if approximateCacheData:
            return json.loads(approximateCacheData)
        
        serializer = methodData.serializer_class(methodData.queryset, many=True)
        data = serializer.data
        
        CacheMethods.setCache(methodData.cacheName, data,timeOut)
        
        return data
    
    def destroyMethod(methodData):
        instance = methodData.get_object()

        instance.delete()

        return status.HTTP_204_NO_CONTENT