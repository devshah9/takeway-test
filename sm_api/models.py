from django.db import models
from datetime import time
# Create your models here.

class Store(models.Model):
    store_id = models.BigIntegerField(primary_key=True)
    timezone_str = models.CharField(max_length=50, default='America/Chicago')

class BusinessHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time_utc = models.TimeField(default=time(0, 0, 0))
    end_time_utc = models.TimeField(default=time(23, 59, 00))

class StoreStatus(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)

class Report(models.Model):
    STATUS_CHOICES = (
        ('running', 'Running'),
        ('complete', 'Complete'),
    )
    status = models.CharField(choices=STATUS_CHOICES, default='running', max_length=10)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    name = models.CharField(max_length=20)