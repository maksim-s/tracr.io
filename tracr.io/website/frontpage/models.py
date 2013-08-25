from django.db import models

# Create your models here.
class EmailSubscription(models.Model):
  email = models.CharField(max_length=100)
