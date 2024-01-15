from django.db import models
from django.contrib.auth.models import User
import uuid

    
class Pendency(models.Model):
    pid = models.CharField(max_length=255 , unique=True)
    tid = models.CharField(max_length=255 , unique=True)
    