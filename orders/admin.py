from django.contrib import admin

# Register your models here.

from .models import Order, ProductPurchase

admin.site.register(Order)

class ProductPurchaseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestamp', 'refunded']
    class Meta:
        model = ProductPurchase

admin.site.register(ProductPurchase, ProductPurchaseAdmin)
