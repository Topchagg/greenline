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

            serializer.save()

            CacheMethods.setCache(f"cleaner-got-order__${date}__${cleanerID}",True,60*3)
            CacheMethods.deleteCache(f"booked-cleaner__${date}__${cleanerID}")

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
            realTime = CacheMethods.getCache(f"order_info_time__${id}")

            data = {"inProcess": False,"salary":realPrice}

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)











class ReturnFreeCleaners(View):
    def get(self, request, *args, **kwargs):
        targetDateStr = request.GET.get("date")

        cleaningTimeStart = request.GET.get("cleaningTimeStart")
        approximateTimeWork = request.GET.get("approximateTimeWork")
    
        freeCleanersCacheName = f"free-cleaners__${targetDateStr}"

        freeCleanersCache = CacheMethods.getCache(freeCleanersCacheName)

        # if freeCleanersCache:
        #     return JsonResponse({"cleaners":json.loads(freeCleanersCache)},status=status.HTTP_200_OK)

        try:
            if not targetDateStr:
                return JsonResponse({"error":"Date is requies"},status=status.HTTP_400_BAD_REQUEST)
            
            try: 
                targetDate = datetime.strptime(targetDateStr, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error":"Invalid date"}, status=status.HTTP_400_BAD_REQUEST)
            
            ordersOnThatDay = Order.objects.filter(date=targetDate)
            
            freeCleaners = Cleaner.objects.exclude(id__in=Subquery(ordersOnThatDay.values("cleaner_id")))
            serialized_data = EmployeePreviewSerializer(freeCleaners, many=True)
            if len(serialized_data.data) > 0:
                CacheMethods.setCache(freeCleanersCacheName,serialized_data.data,3600*24)
                return JsonResponse({"cleaners": serialized_data.data},status=status.HTTP_200_OK)
            else:
                allCleaners = Cleaner.objects.all() 
                serializer = EmployeeWithOrders(allCleaners,many=True,context={"date":targetDate})

                result = canOrderOnThisTime(serializer.data,cleaningTimeStart,approximateTimeWork)
                
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

        if date and idOfCleanerToBook:

            bookedCleanerCacheName = f"booked-cleaner__${date}__${idOfCleanerToBook}"
            freeCleanerCacheName = f"free-cleaners__${date}"

            possiblyBookedUser = CacheMethods.getCache(bookedCleanerCacheName)

            if possiblyBookedUser:
                return JsonResponse({"error":"This cleaner already booked"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                CacheMethods.setCache(bookedCleanerCacheName,idOfCleanerToBook,60*2)
                freeCleaners = json.loads(CacheMethods.getCache(freeCleanerCacheName))
                newCleanerList = []
                deletedCleaner = ""

                for cleaner in freeCleaners:
                    if cleaner["id"] != idOfCleanerToBook:
                        newCleanerList.append(cleaner)
                    else:
                        deletedCleaner = cleaner

                CacheMethods.setCache(freeCleanerCacheName,newCleanerList,60*60)
                
                checkIsOrdered.apply_async((date, idOfCleanerToBook, deletedCleaner), countdown=150)

                return JsonResponse({"ok":"Cleaner was ordered"},status=status.HTTP_200_OK)
            
        else:
            return JsonResponse({"error":"Wrong params was sended"},status.HTTP_400_BAD_REQUEST)
    

    