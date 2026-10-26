from django.db import models

# Create your models here.
class Book(models.Model):
    open_libary_id=models.CharField(max_length=100,unique=True)
    tittle=models.CharField(max_length=255)
    author=models.CharField(max_length=255,blank=True)
    publishyear=models.IntegerField(null=True,blank=True)
    coverurl=models.URLField(blank=True)
    
    def __str__(self):
        return self.tittle

    