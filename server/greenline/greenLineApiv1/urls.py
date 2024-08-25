from django.urls import path,include
from rest_framework import routers

from .views import *

router = routers.SimpleRouter()

router.register(r'preview-employees', PreviewEmployeeViewSet, basename='preview-employee')
router.register(r'employees', EmployeeViewSet, basename='employee')

#

router.register(r'preview-clean-type',PreviewCleanTypeViewSet, basename='preview-clean-type')
router.register(r'clean-type',CleanTypeViewSet, basename='clean-type')

#

router.register(r'preview-wash-liquid',PreviewWashLiquidViewSet,basename='preview-wash-liquid')
router.register(r'wash-liquid', WashLiquidViewSet, basename='wash-liquid')

#

router.register(r'order',MakeOrderViewSet)




urlpatterns = [
    path('',include(router.urls)),
    path('find-free-cleaners/', ReturnFreeCleaners.as_view()),
    path('book-cleaner/',BookCleaner.as_view())
]