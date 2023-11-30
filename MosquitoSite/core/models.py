from django.db import models

# Create your models here.
class MosquitoImages(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="mosquitoes")
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class MosquitoSystem(models.Model):
    id = models.AutoField(primary_key=True)
    secret_key = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="mosquitoes")

    def __str__(self):
        return self.name