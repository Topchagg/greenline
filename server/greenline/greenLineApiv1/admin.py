from django.contrib import admin

from .models import *

# Register your models here.


admin.site.register(Cleaner)
admin.site.register(CleanType)
admin.site.register(Order)
admin.site.register(WashLiquid)
admin.site.register(Sale)
admin.site.register(AdditionalItem)