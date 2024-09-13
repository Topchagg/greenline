import json
import logging
import asyncio

from greenline.celery import app

from greenLineApiv1.utils.CacheMethods import CacheMethods


def checkOrder(date,id):
    cleanerCache = CacheMethods.getCache(f"cleaner-got-order__${date}__${id}")

    if not cleanerCache: # Если истёк таймаут в три минуты и заказ не был подтвержден
        try:
            newBookedCleaners = json.loads(CacheMethods.getCache(f"booked_cleaners__${date}"))

            newBookedCleaners.append(id)

            CacheMethods.setCache(f"booked_cleaners__${date}",newBookedCleaners,3600*24)

            CacheMethods.deleteCache(f"cleaner-got-order__${date}__${id}")

        except Exception as e:
            print(e)
       
        

        
@app.task
def checkIsOrdered(date,id:int) -> None:
    checkOrder(date,id)

@app.task(bind=True)
def calculatePrice(self, id: str, pricePerHr: float, currentPrice: float):
    pricePerSecond = (pricePerHr / 60) / 60
    control_key = f"task_control__${id}"

    CacheMethods.setCache(control_key, "Processing", 60 * 3600)

    currentLocalPrice = currentPrice
    currentTimeInSeconds = 0
    isFirstRender = True

    async def async_loop():
        nonlocal isFirstRender, currentLocalPrice, currentTimeInSeconds
        while True:
            control_status = json.loads(CacheMethods.getCache(control_key))
            if control_status == "stop":
                CacheMethods.setCache(f"order_info_price__${id}", currentLocalPrice, 60 * 5)
                CacheMethods.setCache(f"order_info_time__${id}", currentLocalPrice / pricePerSecond, 60 * 5)
                CacheMethods.deleteCache(control_key)
                break

            currentLocalPrice += pricePerSecond * 10
            currentTimeInSeconds += 10

            CacheMethods.setCache(f"order_info_price__${id}", currentLocalPrice, 60 * 5)
            CacheMethods.setCache(f"order_info_time__${id}", currentLocalPrice / pricePerSecond, 60 * 5)

            await asyncio.sleep(10) if not isFirstRender else asyncio.sleep(10)
            isFirstRender = False

    try:
        asyncio.run(async_loop())
    except Exception as e:
        logging.error(f"Error in calculatePrice task: {str(e)}")
        raise self.retry(exc=e)
