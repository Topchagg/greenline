from django.db import models
from datetime import time

class Cleaner(models.Model):
    name = models.CharField(max_length=30)
    image = models.TextField()
    surname = models.CharField(max_length=30)
    phoneNumber = models.CharField(max_length=15)
    taskPerDay = models.IntegerField()
    startWorkDay = models.TimeField()
    endWorkDay = models.TimeField()
    rating = models.FloatField()
    isHaveOurItems = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.surname}"


class CleanType(models.Model):
    name = models.CharField(max_length=30)
    image = models.TextField()
    description = models.TextField()
    whatCleanerDo = models.TextField()
    pricePerHr = models.IntegerField()
    amountOrders = models.IntegerField()
    time = models.TimeField()  # medianTime
    price = models.IntegerField()  # medianPrice
    liveRoom = models.IntegerField()  # timeLiveRoomClean
    kitchen = models.IntegerField()  # timeKitchenClean
    corridor = models.IntegerField()  # TimeCleanCorridor
    bathroom = models.IntegerField()  # BathroomClean
    washLiquidUsage = models.IntegerField()  # Medium usage
    employeeSalary = models.IntegerField()
    marge = models.IntegerField()
    amortisation = models.IntegerField()
    transport = models.IntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE) #
    orderType = models.ForeignKey(CleanType, on_delete=models.CASCADE) #

    # withTransport = models.BooleanField(default=True)
    inProcess = models.BooleanField(default=False) 
    isDone = models.BooleanField(default=False)

    phoneNumber = models.CharField(max_length=15) #
    address = models.CharField(max_length=150) #
    name = models.CharField(max_length=30) #

    startTask = models.TimeField() #
    endTask = models.TimeField() #
    breakTime = models.TimeField(default='01:00') #
    # readyToNewTask = models.TimeField() #

    cleaningTime = models.TimeField(null=True) #
    salary = models.IntegerField(null=True) #

    isGood = models.BooleanField(default=True) #
    message = models.TextField(default='') #

    approximateTime = models.TimeField() #
    approximatePrice = models.IntegerField()  #

    date = models.DateField()

    def __str__(self):
        return f"Order #{self.pk} by {self.cleaner}"


class WashLiquid(models.Model):
    name = models.CharField(max_length=20)
    link = models.TextField()
    image = models.TextField()
    price = models.IntegerField()
    volume = models.IntegerField()
    totalClean = models.IntegerField()  # medium usage per clean task
    basicClean = models.IntegerField()  # medium usage per clean task
    supportClean = models.IntegerField()  # medium usage per clean task

    def __str__(self):
        return self.name


class Sale(models.Model):
    name = models.CharField(max_length=50)
    percent = models.IntegerField()
    sale = models.IntegerField()
    description = models.TextField()

    isActive = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AdditionalItem(models.Model):
    name = models.CharField(max_length=30)
    approximateTime = models.TimeField()
    approximateCost = models.IntegerField()

    def __str__(self):
        return self.name



class WorkDay(models.Model):
    owner = models.ForeignKey(Cleaner, on_delete=models.PROTECT)
    order = models.ForeignKey(Order,on_delete=models.PROTECT)
    date = models.DateField()

# 1. Получить всех клинеров
# 2. Получить все Ордеры клинеров на эту ключевую дату
# 3. Разделить клинеров у которых есть ордер на эту дату а у кого нет
# 4. Вернуть список клинеров у которых нет ордера на эту дату на клиент
# 5. После отправки айди клиента уже создать нужный workDay и Order и привязать выбранного клинера
# 6. 