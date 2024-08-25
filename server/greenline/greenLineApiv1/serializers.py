from rest_framework.serializers import ModelSerializer

from .models import *

class EmployeePreviewSerializer(ModelSerializer):
    class Meta:
        model = Cleaner
        fields = ['id','name','surname','rating','image']

class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Cleaner
        fields = '__all__'

#
class CleanTypePreviewSerializer(ModelSerializer):
    class Meta:
        model = CleanType
        fields = ['name','pricePerHr','image','id']

class CleanTypeSerializer(ModelSerializer):
    class Meta:
        model = CleanType
        fields = '__all__'
#

class WashLiquidPreviewSerializer(ModelSerializer):
    class Meta:
        model = WashLiquid
        fields = ['link','image','price','volume']

class WashLiquidSerializer(ModelSerializer):
    class Meta:
        model = WashLiquid
        fields = '__all__'


class AdditionalItemSerializer(ModelSerializer):
    class Meta:
        model = AdditionalItem
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'