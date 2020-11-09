from django.contrib import admin
from .models import Attendance_Logs, Sessions, Device

admin.site.register(Attendance_Logs)
admin.site.register(Sessions)
admin.site.register(Device)