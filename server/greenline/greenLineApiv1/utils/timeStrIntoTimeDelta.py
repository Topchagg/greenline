from datetime import timedelta


def timeStrIntoTimeDelta(timeStr):
    hrs,mints = map(int,timeStr[:4].split(":"))
    valueToReturn = timedelta(hours=hrs,minutes=mints)

    return valueToReturn