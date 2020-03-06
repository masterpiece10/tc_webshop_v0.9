from django.conf import settings
from django.db import models
from django.shortcuts import reverse

# Create your models here.
from billing.models import BillingProfile


ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

User = settings.AUTH_USER_MODEL

class Address(models.Model):
    nickname            = models.CharField(max_length=120, null=True, blank=True)
    name                = models.CharField(max_length=120, null=True, blank=True, help_text='Shipping to? Who is it for?')
    billing_profile     = models.ForeignKey(BillingProfile, null=True, on_delete=models.SET_NULL)
    address_type        = models.CharField(max_length=120, choices=ADDRESS_TYPES)
    address_line_1      = models.CharField(max_length=120)
    address_line_1      = models.CharField(max_length=120)
    address_line_2      = models.CharField(max_length=120, blank=True, null=True)
    address_line_3      = models.CharField(max_length=120, blank=True, null=True)
    city                = models.CharField(max_length=120)
    country             = models.CharField(max_length=120, default="Hong Kong")
    state               = models.CharField(max_length=120, blank=True, null=True)
    zip_code            = models.CharField(max_length=120)

    def __str__(self):
        if self.nickname:
            return str(self.nickname) + ' ' + str(self.name)
        return str(self.address_line_1)

    def get_address(self):
        return "{line1}\n{line2}\n{line3}\n{city}\n{state}{zip_code}\n{country}".format(
            line1    = self.address_line_1,
            line2    = self.address_line_2 or "",
            line3    = self.address_line_3 or "",
            city     = self.city,
            state    = self.state or "",
            zip_code = self.zip_code,
            country  = self.country,
        )
    
    def get_short_address(self):
        for_name = ""
        if self.name is not None:
            for_name = str(self.name)
        if self.nickname:
            for_name = f"{self.nickname} | {for_name}"
        context = f"{for_name}\n{self.address_line_1}, {self.city}"
        print(context)
        return context

    def get_absolute_url(self):
        return reverse("addresses:address-change", kwargs={"pk": self.pk})
    