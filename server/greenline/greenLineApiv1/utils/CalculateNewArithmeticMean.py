

def CalculateNewArithmeticMean(amount:int,oldArithmeticMean:int,newValue:int) -> int:

    newAmount = amount + 1

    newArithmeticMean = (oldArithmeticMean * amount + newValue) / newAmount

    return newArithmeticMean