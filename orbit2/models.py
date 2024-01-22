from django.db import models
from django.contrib.auth.models import User
import uuid

class Pendency(models.Model):
    vertical = models.CharField(max_length=255 , null = True , blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    brand = models.CharField(max_length=50, blank=True , null=True)
    keywords = models.CharField(max_length=255, blank=True , null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    pid = models.CharField(max_length=255)
    tid = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = self.tid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    casper_id = models.CharField(max_length=8)
    image = models.ImageField(default="default.jpg" , upload_to="profile_pics" )

    def __str__(self):
        return f"{self.user.username} Profile"
    

class physicalOrphan(models.Model):
    oid = models.CharField(max_length=255)
    tid = models.OneToOneField(Pendency , on_delete=models.CASCADE , default=None , blank=True)
    image = models.ImageField(upload_to='orphan_images/', blank=True, null=True)
    def __str__(self):
        return self.tid

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    query = models.CharField(max_length=255)
    filename = models.CharField(max_length=255 ,  blank=True, null=True)
    uuid = models.CharField(editable=False, unique=True , max_length=255 , blank=True , null=True)
    reconciled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.query}"

    class Meta:
        ordering = ['-timestamp']

class ReconciliationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tid = models.CharField(max_length=255)
    reconciled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reconciled TID {self.tid} at {self.reconciled_at}"



