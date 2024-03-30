from django.db import models
from django.utils import timezone

class System(models.Model):
    id = models.AutoField(primary_key=True)
    secret_key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="system")
    coverage = models.ForeignKey('AreaCoverage', related_name="systems", on_delete=models.CASCADE)
   
    location_name = models.CharField(max_length=100)
    location_latitude = models.FloatField()
    location_longitude = models.FloatField()
    location_radius = models.FloatField()

    @property
    def latest_status(self):
        last_status_date = self.status.last()
        
        if not last_status_date:
            return "Inactive"
        
        current_time = timezone.now()

    
        if (current_time - last_status_date.last_updated).total_seconds() < 60:
            return "Active"
        elif (current_time - last_status_date.last_updated).total_seconds() < 300:
            return "Delayed"
        else:
            return "Inactive"


    def __str__(self):
        return self.name
    
class SystemStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.BooleanField()
    system = models.ForeignKey('System', on_delete=models.CASCADE, related_name="status")
    last_updated = models.DateTimeField(auto_now=True)

class SystemFumigation(models.Model):
    id = models.AutoField(primary_key=True)
    system = models.ForeignKey('System', on_delete=models.CASCADE)
    fumigation_date = models.DateTimeField()
    

class SystemWaterLevel(models.Model):
    id = models.AutoField(primary_key=True)
    system = models.ForeignKey('System', on_delete=models.CASCADE)
    water_level = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

class AreaCoverage(models.Model):
    id = models.AutoField(primary_key=True)

    area_name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="mosquitoes")
    area_latitude = models.FloatField()
    area_longitude = models.FloatField()

    def __str__(self):
        return self.area_name

class Images(models.Model):
    id = models.AutoField(primary_key=True)

    system = models.ForeignKey('System', on_delete=models.CASCADE)
    area = models.ForeignKey('AreaCoverage', on_delete=models.CASCADE, related_name="images")

    photo = models.ImageField(upload_to="mosquitoes")
    date_uploaded = models.DateTimeField(auto_now_add=True)
    detected_mosquito_count = models.IntegerField()

    prediction_time = models.FloatField()


    def __str__(self):
        return f"{self.system.name} - {self.area.area_name} - {self.date_uploaded}"
    