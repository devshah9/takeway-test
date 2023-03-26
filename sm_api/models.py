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
