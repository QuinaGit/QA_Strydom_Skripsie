from django.contrib.auth.models import User
from django.core.validators     import MaxValueValidator, MinValueValidator
from django.db                  import models
from django.urls                import reverse
from django.utils               import timezone

class Device(models.Model):
    unit_name           = models.CharField(max_length=50)
    software_version    = models.CharField(max_length=50)
    last_update         = models.DateTimeField()
    last_upload         = models.DateTimeField(default=timezone.now)

class Sessions(models.Model):
    start_datetime      = models.DateTimeField()
    end_datetime        = models.DateTimeField()
    session_id          = models.CharField(max_length=14)
    lecturer            = models.ForeignKey(User, on_delete=models.CASCADE)
    device              = models.ForeignKey(Device, on_delete=models.CASCADE)

class Logs(models.Model):
    usnumber            = models.PositiveIntegerField(validators=[MinValueValidator(10000000),MaxValueValidator(99999999)])
    date                = models.DateTimeField()
    session             = models.ForeignKey(Sessions, on_delete=models.CASCADE)

class ClassList(models.Model):
    name                = models.CharField(max_length=100)
    usnumber            = models.PositiveIntegerField(validators=[MinValueValidator(10000000),MaxValueValidator(99999999)])
    last_modified       = models.DateTimeField(default=timezone.now)
