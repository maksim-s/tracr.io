from django.db import models

class ModelA(models.Model):
  boolean = models.NullBooleanField(null=True, blank=True)
  text = models.TextField(null=True, blank=True)
  date = models.DateTimeField(null=True, blank=True)
  integer = models.IntegerField(null=True, blank=True)

  # Related fields.
  foreign = models.ForeignKey('ModelB', null=True, blank=True,
                              related_name='o2m')
  m2m = models.ManyToManyField('ModelB', null=True, blank=True,
                               related_name='m2m')
  o2o = models.OneToOneField('ModelB', null=True, blank=True)


class ModelB(models.Model):
  a = models.ForeignKey(ModelA, null=True, blank=True, related_name='o2m')
