import json

from django.views import View
from rest_framework import viewsets,mixins
from rest_framework.response import Response
from django.db.models import Subquery
from django.http import JsonResponse
from datetime import datetime
from rest_framework import status

from greenline.celery import app

from celery.result import AsyncResult

from .tasks import *

from .models import *
from .serializers import *
from .utils.ViewMethods import ViewMethods
from .utils.CacheMethods import CacheMethods

class PreviewEmployeeViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Cleaner.objects.all()
    serializer_class = EmployeePreviewSerializer
    cacheName = 'Employees'

    def list(self, request, *args, **kwargs):
        data = ViewMethods.listMethod(self,60*120)
        return Response(data)

    def destroy(self,request,*args,**kwargs):
        pass

class EmployeeViewSet(  
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
    ):
    queryset = Cleaner.objects.all()
    serializer_class = EmployeeSerializer

#

class PreviewCleanTypeViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = CleanType.objects.all()
    serializer_class = CleanTypePreviewSerializer
    cacheName = 'cleanType'

    def list(self, request, *args, **kwargs):
        data = ViewMethods.listMethod(self,60*120)
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
#

class PreviewWashLiquidViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = WashLiquid.objects.all()
    serializer_class = WashLiquidPreviewSerializer
    cacheName = 'washLiquids'


    def list(self, request, *args, **kwargs):

        data = ViewMethods.listMethod(self,60*120)
        return Response(data)

class WashLiquidViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    queryset = WashLiquid.objects.all()
    serializer_class = WashLiquidSerializer
    cacheName = 'Clean-type__$'

    def retrieve(self,request,*args,**kwargs):
        instane = self.get_object()
        self.CacheName += str(instane.id)
        data = ViewMethods.listMethod(self,3600*72)
        return Response(data)

class AdditionalItemViewSet(viewsets.ModelViewSet):
    queryset = AdditionalItem.objects.all()
    serializer_class = AdditionalItemSerializer

        

class MakeOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)


        if serializer.is_valid():
            serializer.save()

            CacheMethods.setCache(f"cleaner-got-order__${serializer.data['date']}__${serializer.data['cleaner']}",True,60*3)
            CacheMethods.deleteCache(f"booked-cleaner__${serializer.data['date']}__${serializer.data['cleaner']}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class ManipulateWithOrder(viewsets.ViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # def update(self, request, *args, **kwargs):
    #     id = request.GET.get('id')
    #     is_start = request.GET.get('isStart')

    #     if not id:
    #         return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
    #     try:
    #         instance = Order.objects.get(pk=id)
    #     except Order.DoesNotExist:
    #         return Response({"error":"Not found"})
        
    #     instance.inProcess = json.loads(is_start)
        
    #     serialized = self.serializer_class(instance, data=request.data, partial=True)
        
    #     if serialized.is_valid():
    #         if(is_start):
    #             calculatePrice(id,instance.pricePerHr)
    #         else:
    #             taskId = CacheMethods.getCache(f"price__${id}")
    #             result = AsyncResult(taskId,app=app)
    #             result.revoke(terminate=True,signal="SIGTERM")
    #             serialized_with_data = self.serializer_class(instance,data=request.data, partial=True)
    #             if serialized_with_data.is_valid():

    #         serialized.save()
    #         return Response(serialized.data)
    #     else:
    #         return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)



class ReturnFreeCleaners(View):
    def get(self, request, *args, **kwargs):
        targetDateStr = request.GET.get('date')

        freeCleanersCache = CacheMethods.getCache(f'free-cleaners__${targetDateStr}')

        if freeCleanersCache:
            return JsonResponse({'cleaners':json.loads(freeCleanersCache)},status=status.HTTP_200_OK)

        try:

            if not targetDateStr:
                return JsonResponse({'error':'Date is requies'},status=status.HTTP_400_BAD_REQUEST)
            
            try: 
                targetDate = datetime.strptime(targetDateStr, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error':'Invalid date'}, status=status.HTTP_400_BAD_REQUEST)
            
            ordersOnThatDay = Order.objects.filter(date=targetDate)
            
            freeCleaners = Cleaner.objects.exclude(id__in=Subquery(ordersOnThatDay.values('cleaner_id')))
            serialized_data = EmployeePreviewSerializer(freeCleaners, many=True)

            CacheMethods.setCache(f"free-cleaners__${targetDateStr}",serialized_data.data,3600*24)

            return JsonResponse({'cleaners': serialized_data.data},status=status.HTTP_200_OK)
        
        except json.JSONDecodeError:
            return JsonResponse({"error":"Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        

class BookCleaner(View):
    def get(self,request,*args,**kwargs):
        idOfCleanerToBook = int(request.GET.get('id'))
        date = request.GET.get('date')

        if date and idOfCleanerToBook:

            possiblyBookedUser = CacheMethods.getCache(f"booked-cleaner__${date}__${idOfCleanerToBook}")

            if possiblyBookedUser:
                return JsonResponse({"error":"This cleaner already booked"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                CacheMethods.setCache(f"booked-cleaner__${date}__${idOfCleanerToBook}",idOfCleanerToBook,60*2)
                freeCleaners = json.loads(CacheMethods.getCache(f"free-cleaners__${date}"))
                newCleanerList = []
                deletedCleaner = ''

                for cleaner in freeCleaners:
                    if cleaner['id'] != idOfCleanerToBook:
                        newCleanerList.append(cleaner)
                    else:
                        deletedCleaner = cleaner

                CacheMethods.setCache(f"free-cleaners__${date}",newCleanerList,60*60)
                
                checkIsOrdered.apply_async((date, idOfCleanerToBook, deletedCleaner), countdown=150)

                return JsonResponse({"ok":"Cleaner was ordered"},status=status.HTTP_200_OK)
            
        else:
            return JsonResponse({"error":"Wrong params was sended"},status.HTTP_400_BAD_REQUEST)
    

    