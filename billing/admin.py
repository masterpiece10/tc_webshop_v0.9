from django.contrib import admin

# Register your models here.

from .models import BillingProfile, Card, Charge

class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ["email", "id", "user", ]

    class Meta:
        model = BillingProfile

admin.site.register(BillingProfile, BillingProfileAdmin)

admin.site.register(Card)

admin.site.register(Charge)