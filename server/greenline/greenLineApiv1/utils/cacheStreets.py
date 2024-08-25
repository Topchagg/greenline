from django.core.cache import cache
from json import dumps

def cacheSomething(key:str,value:str) -> None:

    valueToSet = dumps(value,ensure_ascii=False)

    cache.set(key,valueToSet,60*30)