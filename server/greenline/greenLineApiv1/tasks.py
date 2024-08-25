import json

import time

from greenline.celery import app

from greenLineApiv1.utils.CacheMethods import CacheMethods


def checkOrder(date,id,cleanerToBack):
    cleanerCache = CacheMethods.getCache(f"cleaner-got-order__${date}__${id}")
    if cleanerCache: # Если подтвердили ордер
        pass
    else: # Если истёк timeout
        freeCleaners = json.loads(CacheMethods.getCache(f"free-cleaners__${date}"))
        freeCleaners.append(cleanerToBack)
        CacheMethods.setCache(f"free-cleaners__${date}",freeCleaners,60*60)

        
@app.task
def checkIsOrdered(date,id:int, cleanerToBack:dict) -> None:
    checkOrder(date,id,cleanerToBack)

@app.task
def calculatePrice(id: str, pricePerHer: float):
    pricePerSecond = (pricePerHer / 60) / 60
    
    CacheMethods.setCache(f"price__{id}", 0, 60*60)
    
    try:
        while True:
            if self.request.called_directly or self.request.terminated:
                print(f"Task {id} has been terminated.")
                break
            
            getCache = json.loads(CacheMethods.get(f"price__{id}"))
            newData = getCache + pricePerSecond
            CacheMethods.setCache(f"price__{id}", newData, 60*60)
            
            time.sleep(1)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise self.retry(exc=e, countdown=60)