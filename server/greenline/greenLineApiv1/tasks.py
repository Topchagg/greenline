import json
import logging
import time

from greenline.celery import app

from greenLineApiv1.utils.CacheMethods import CacheMethods


def checkOrder(date,id,cleanerToBack):
    cleanerCache = CacheMethods.getCache(f"cleaner-got-order__${date}__${id}")
    if cleanerCache: # Если подтвердили ордер
        pass
    else: # Если истёк timeout
        freeCleaners = CacheMethods.getCache(f"free-cleaners__${date}")
        if freeCleaners:
            freeCleaners = json.loads(freeCleaners)
            freeCleaners.append(cleanerToBack)
            CacheMethods.setCache(f"free-cleaners__${date}",freeCleaners,60*60)


        
@app.task
def checkIsOrdered(date,id:int, cleanerToBack:dict) -> None:
    checkOrder(date,id,cleanerToBack)

@app.task
def calculatePrice(id:str,pricePerHr:float,currentPrice:float):
    pricePerSecond = (pricePerHr/60) / 60

    control_key = f"task_control__${id}"

    CacheMethods.setCache(control_key,"Proccessing",60*3600)

    currentLocalPrice = currentPrice

    try: 
        while True:
            control_status = json.loads(CacheMethods.getCache(control_key))
            if control_status == "stop":
                CacheMethods.setCache(f"order_info_price__${id}",currentLocalPrice,60*5)
                CacheMethods.setCache(f"order_info_time__${id}", currentLocalPrice/pricePerSecond, 60*5)
                CacheMethods.deleteCache(f"task_control__${id}")
                break
            currentLocalPrice += pricePerSecond
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in calculatePrice task: {str(e)}")