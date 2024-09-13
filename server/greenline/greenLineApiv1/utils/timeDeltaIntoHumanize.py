def timeDeltaIntoHumanize(timeDeltaObject):
    totalSeconds = int(timeDeltaObject.total_seconds())
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60

    return f"{hours:02}:{minutes:02}"
    