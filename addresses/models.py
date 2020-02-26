from django.db import models

# Create your models here.
from billing.models import BillingProfile

ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)

class Address(models.Model):
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
        return str(self.billing_profile)

    def get_address(self):
        return "{line1}\n{line2}\n{line3}\n{city}\n{state}{zip_code}\n{country}".format(
            line1    = self.address_line_1,
            line2    = self.address_line_2 or "",
            line3    = self.address_line_3 or "",
            city     = self.city,
            state    = self.state,
            zip_code = self.zip_code,
            country  = self.country,
        )