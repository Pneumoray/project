from django.db import models

# Create your models here.
class Document(models.Model):
    xray = models.FileField(upload_to='xrays/')

    def __str__(self):
        return self.xray