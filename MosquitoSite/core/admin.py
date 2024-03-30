from django.contrib import admin
from .models import System, SystemStatus, SystemFumigation, SystemWaterLevel, AreaCoverage, Images

admin.site.register(System)
admin.site.register(SystemStatus)
admin.site.register(SystemFumigation)
admin.site.register(SystemWaterLevel)
admin.site.register(AreaCoverage)
admin.site.register(Images)


# Register your models here.
