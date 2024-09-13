from datetime import timedelta

from .findTimeCut import findTimeCut
from .timeStrIntoTimeDelta import timeStrIntoTimeDelta
from greenLineApiv1.serializers import *

def canOrderOnThisTime(cleaners, timeStartCleaningObject,approximateCleanTime,bookedCleaners):

    timeStartCleaningObject = timeStrIntoTimeDelta(timeStartCleaningObject)
    approximateCleanTime = timeStrIntoTimeDelta(approximateCleanTime) + timedelta(hours=1)

    timeEndCleaningObject = timeStartCleaningObject + approximateCleanTime

    if timeEndCleaningObject > timeStartCleaningObject:
        cleanerThatCanClean = []
        globalTimes = []

        for cleaner in cleaners:
            localTimes = []
            isPossibleToBookThisCleaner = True
            if cleaner['id'] not in bookedCleaners and len(cleaner['orders']) < 3 and len(cleaner['orders']) >= 1:
                for order in cleaner["orders"]:
                    orderTimeStart = timeStrIntoTimeDelta(order["startTask"])
                    orderTimeEnd = timeStrIntoTimeDelta(order["endTask"])

                    orderTimings = {"orderTimeStart": order['startTask'], "orderTimeEnd": order['endTask']}
                    localTimes.append(orderTimings)

                    if (orderTimeStart < timeEndCleaningObject and timeStartCleaningObject < orderTimeEnd):
                        isPossibleToBookThisCleaner = False
                            
                    else:
                        isPossibleToBookThisCleaner = False

                    if isPossibleToBookThisCleaner:
                        cleanerThatCanClean.append(cleaner['id'])
                    globalTimes.append(localTimes)

            elif len(cleaner['orders']) == 0:
                cleanerThatCanClean.append(cleaner['id'])

        if len(cleanerThatCanClean) > 0:
            return {"data":cleanerThatCanClean,"isListOfId":True}
        else:
            result = findTimeCut(globalTimes, approximateCleanTime)

            tupleSet = {tuple(d.items()) for d in result}
            dictSet = [dict(t) for t in tupleSet]
            
            return {"data":dictSet,"isListOfId":False}
    else:
        return "Time-end cannot be less than time-start"
