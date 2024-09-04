def checkIsInDiapasone(t, l):
    if t[0] < l[1] and l[0] < t[1]:
        return True
    return False