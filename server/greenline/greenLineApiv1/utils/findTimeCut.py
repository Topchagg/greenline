from datetime import timedelta


from .addCutsToList import addCutsToList
from .timeStrIntoTimeDelta import timeStrIntoTimeDelta

def findTimeCut(timeLines, approximateCleanTime):
    possibleCuts = []
    possibleEarlest = timedelta(hours=6, minutes=0)
    possibleLatest = timedelta(hours=22, minutes=0)


    for listOfCuts in timeLines:
        for cut in listOfCuts:
            operateOrderTimeStart = timeStrIntoTimeDelta(cut["orderTimeStart"])


            operateOrderTimeEnd = timeStrIntoTimeDelta(cut["orderTimeEnd"])

            possibleEarlestTaskStart = operateOrderTimeStart - approximateCleanTime
            possibleEarlestTaskEnd = possibleEarlestTaskStart + approximateCleanTime

            possibleLatestTaskStart = operateOrderTimeEnd + timedelta(hours=1)
            possibleLatestTaskEnd = possibleLatestTaskStart + approximateCleanTime

            if possibleEarlest <= possibleEarlestTaskStart < possibleLatest:
                addCutsToList(listOfCuts, possibleCuts,[possibleEarlestTaskStart, possibleEarlestTaskEnd])

            if possibleEarlest <= possibleLatestTaskStart < possibleLatest:
                addCutsToList(listOfCuts, possibleCuts,[possibleLatestTaskStart, possibleLatestTaskEnd])

    return possibleCuts

