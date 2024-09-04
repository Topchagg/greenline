def timeDeltaIntoHumanize(timeDeltaObject):
    totalSeconds = int(timeDeltaObject.total_seconds())
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60

    if len(str(hours)) == 1 and len(str(minutes)) == 1:
        return f"0{hours}:{minutes}0"
    elif len(str(hours)) == 1 and len(str(minutes)) != 1:
        return f"0{hours}:{minutes}"
    elif len(str(hours)) != 1 and len(str(minutes)) == 1:
        return f"{hours}:{minutes}0"
    