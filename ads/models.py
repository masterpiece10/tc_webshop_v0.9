from django.conf import settings
from django.db import models

from products.models import Product

User = settings.AUTH_USER_MODEL

# Create your models here.

"""
Ad model:

product ForeignKey
views
clicks
timeframe
    datestart --> from date to date post save product receiver?
    dateend
timestamp

"""

class Ads(models.Model):
    product         = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    user            = models.ManyToManyField(User, blank=True)
    views           = models.IntegerField(blank=True, null=True, default=0)
    clicks          = models.IntegerField(blank=True, null=True, default=0)
    date_started    = models.DateTimeField(auto_now_add=True, auto_now=False)
    date_ended      = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp       = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return str(self.product.title) + " | " + str(self.date_started)

    class Meta:
        verbose_name_plural = "Ads"