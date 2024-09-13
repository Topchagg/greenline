import json
import time

from django.views import View
from rest_framework import viewsets,mixins
from rest_framework.response import Response
from django.db.models import Subquery
from django.http import JsonResponse
from datetime import datetime
from rest_framework import status
from django.shortcuts import get_object_or_404

from .tasks import *

from .models import *
from .serializers import *
from .utils.ViewMethods import ViewMethods
from .utils.CacheMethods import CacheMethods
from .utils.SearchingFreeCleaners import *
from .utils.timeDeltaIntoHumanize import timeDeltaIntoHumanize
from .utils.CalculateNewArithmeticMean import CalculateNewArithmeticMean




class PreviewEmployeeViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Cleaner.objects.all()
    serializer_class = EmployeePreviewSerializer
    cacheName = "Employees"

    def list(self, request, *args, **kwargs):
        data = ViewMethods.getMethod(self,60*120)
        return Response(data)

class EmployeeViewSet(  
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
    ):
    queryset = Cleaner.objects.all()
    serializer_class = EmployeeSerializer
    cacheName = "employee_item_info__$"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.cacheName += str(instance.id)
        data = ViewMethods.getMethod(self,60*120)
        return Response(data[0],status=status.HTTP_200_OK)
#





class PreviewCleanTypeViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = CleanType.objects.all()
    serializer_class = CleanTypePreviewSerializer
    cacheName = "clean_types"

    def list(self, request, *args, **kwargs):
        data = ViewMethods.getMethod(self,60*120)
        return Response(data)

class CleanTypeViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
    ):
    queryset = CleanType.objects.all()
    serializer_class = CleanTypeSerializer
    cacheName = "clean-type__$"

    def retrieve(self,request,*args,**kwargs):
        instane = self.get_object()
        self.cacheName += str(instane.id)
        data = ViewMethods.getMethod(self,3600*72)
        return Response(data[0],status=status.HTTP_200_OK)
#





class PreviewWashLiquidViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = WashLiquid.objects.all()
    serializer_class = WashLiquidPreviewSerializer
    cacheName = "wash_liquids"


    def list(self, request, *args, **kwargs):
        data = ViewMethods.getMethod(self,60*120)
        return Response(data)


class WashLiquidViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin
):
    queryset = WashLiquid.objects.all()
    serializer_class = WashLiquidSerializer




class AdditionalItemViewSet(viewsets.ModelViewSet):
    queryset = AdditionalItem.objects.all()
    serializer_class = AdditionalItemSerializer





class MakeOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            date = serializer.data['date']
            cleanerID = serializer.data['cleaner']
            
            bookedCleaners = CacheMethods.getCache(f"booked_cleaners__${date}")

            if bookedCleaners:

                try:
                    bookedCleaners = json.loads(bookedCleaners)
                    newBookedCleaners = []

                    for i in bookedCleaners:
                        if cleanerID != i:
                            newBookedCleaners.append()

                    CacheMethods.setCache(f"booked_cleaners__${date}",newBookedCleaners,3600*24)
                    CacheMethods.setCache(f"cleaner-got-order__${date}__${cleanerID}","booked",60*5)

                except Exception:
                    return Response({"error":"Something went wrong"},status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({"Error":"Invalid data"},status=status.HTTP_400_BAD_REQUEST)
        








class ManipulateWithOrder(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        id = request.data["id"]
        action = request.data["action"]

        if not id or not action:
            return Response({"error": "ID and action are required"}, status=status.HTTP_400_BAD_REQUEST)

        instance = get_object_or_404(Order, pk=id)

        if action == "start" and instance.inProcess:
            return Response({"error":"Process is already started"}, status=status.HTTP_400_BAD_REQUEST)
        elif action == "stop" and instance.inProcess == False:
            return Response({"Error":"Task isn't in process to stop it"}, status=status.HTTP_400_BAD_REQUEST)

        if action == "start":
            cleanTypeInstance = CleanType.objects.get(pk=instance.orderType.id)
            calculatePrice.apply_async(args=[id, cleanTypeInstance.pricePerHr,instance.salary])
            data = {"inProcess": True}

        elif action == "stop":
            time.sleep(1)
            CacheMethods.setCache(f"task_control__${id}","stop",60)

            realPrice = CacheMethods.getCache(f"order_info_price__${id}")
            realTime = timedelta( seconds = int(CacheMethods.getCache(f"order_info_time__${id}")))

            data = {"inProcess": False,"priceToPay":realPrice,"cleaningTime":timeDeltaIntoHumanize(realTime)}
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ConfirmEndOfTask(viewsets.GenericViewSet,mixins.UpdateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    clean_type_serializer_class = CleanTypeSerializer

    def update(self,request,*args,**kwargs):
        
        choicedObject = self.get_object()

        try:
            if choicedObject:
                serializedOrder = self.serializer_class(choicedObject,many=False)
                dataOfOrder = serializedOrder.data

                neededCleanType = CleanType.objects.get(pk=dataOfOrder['orderType'])
                serializedCleanOfType = self.clean_type_serializer_class(neededCleanType,many=False)

                dataOfCleanType = serializedCleanOfType.data

                newArthimeticMeanPrices = CalculateNewArithmeticMean(dataOfCleanType['amountOrders'],dataOfCleanType['price'],dataOfOrder['priceToPay'])

                newOrderData = {"isDone":True}
                newCleanTypeData = {"price":int(newArthimeticMeanPrices),
                                    "time":'00:00:00',
                                    "amountOrders":int(dataOfCleanType.get("amountOrders")) + 1}

                updatedSerializedCleanType = self.clean_type_serializer_class(neededCleanType,data=newCleanTypeData,partial=True)
                updatedSerializedOrder = self.serializer_class(choicedObject,data=newOrderData,partial=True)


                if updatedSerializedOrder.is_valid() and updatedSerializedCleanType.is_valid():
                    
                    updatedSerializedOrder.save()
                    updatedSerializedCleanType.save()

                    return Response(
                        {"ok":"Is updated",
                         "data":{
                            "Order":updatedSerializedOrder.data,
                            "CleanType":updatedSerializedCleanType.data
                        }},
                        status=status.HTTP_200_OK)
                else:
                    return Response({"error":"Data isn't valid"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Order wasn't found"},status=status.HTTP_404_NOT_FOUND)
            
        except Exception:
            return Response({"error": f"Unpredictable error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class ReturnFreeCleaners(View):
    def get(self, request, *args, **kwargs):
        targetDateStr = request.GET.get("date")

        cleaningTimeStart = request.GET.get("startTask")
        approximateTimeWork = request.GET.get("approximateTime")

        try:
            if not targetDateStr:
                return JsonResponse({"error":"Date is requies"},status=status.HTTP_400_BAD_REQUEST)
            try: 
                targetDate = datetime.strptime(targetDateStr, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error":"Invalid date"}, status=status.HTTP_400_BAD_REQUEST)

            allCleaners = Cleaner.objects.all() 
            serializer = EmployeeWithOrders(allCleaners,many=True,context={"date":targetDate})

            bookedCleaners = CacheMethods.getCache(f"booked_cleaners__${targetDateStr}")

            if bookedCleaners:
                bookedCleaners = json.loads(bookedCleaners)
            else:
                bookedCleaners = []

            result = canOrderOnThisTime(serializer.data,cleaningTimeStart,approximateTimeWork,bookedCleaners)

            if result["isListOfId"]:

                findedCleaners = Cleaner.objects.filter(id__in=result["data"])
                serializer = EmployeePreviewSerializer(findedCleaners,many=True)
                
                return JsonResponse({"result":serializer.data},status=status.HTTP_200_OK)

            return JsonResponse({"result":result["data"]},status=status.HTTP_200_OK)
        
        except json.JSONDecodeError:
            return JsonResponse({"error":"Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        







class BookCleaner(View):
    def get(self,request,*args,**kwargs):
        idOfCleanerToBook = int(request.GET.get("id"))
        date = request.GET.get("date")

        if idOfCleanerToBook and date:
            get_object_or_404(Cleaner,pk=idOfCleanerToBook)

            bookedCleaners = CacheMethods.getCache(f"booked_cleaners__${date}")
    
            if bookedCleaners:
                bookedCleaners = json.loads(bookedCleaners)
                bookedCleaners.append(idOfCleanerToBook)
                CacheMethods.setCache(f"booked_cleaners__${date}",bookedCleaners,3600*24)
            else:
                CacheMethods.setCache(f"booked_cleaners__${date}",[idOfCleanerToBook],3600*24)

            checkOrder.apply_async((date,idOfCleanerToBook),countdown=150)
            
            return JsonResponse({"ok":"Is booked"},status=status.HTTP_200_OK)

        else:
            return JsonResponse({"error":"Wrong data"},status=status.HTTP_400_BAD_REQUEST)
