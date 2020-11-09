from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Sessions(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField() 
    scan_count = models.PositiveIntegerField()
    session_id = models.CharField(max_length=50)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)

class Attendance_Logs(models.Model): 
    name = models.CharField(max_length=100)
    usnumber = models.PositiveIntegerField()
    date = models.DateTimeField()
    session_id = models.ForeignKey(Sessions, on_delete=models.CASCADE)

class Device(models.Model):
    unit_name = models.CharField(max_length=50)
    software_version = models.CharField(max_length=50)
    last_update = models.DateTimeField()
    last_upload = models.DateTimeField(default=timezone.now)
