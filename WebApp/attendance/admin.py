from django.contrib import admin
from .models import Logs, Sessions, Device, ClassList

admin.site.register(Logs)
admin.site.register(Sessions)
admin.site.register(Device)
admin.site.register(ClassList)