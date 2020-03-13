from django.contrib import admin
from.models import Product, ProductFile, ProductImage, Variation

# Register your models here.
class ProductFileInLine(admin.TabularInline):
    model = ProductFile
    extra = 1

class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariationInLine(admin.TabularInline):
    model = Variation
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display    = ['__str__', 'slug',]
    inlines         = [VariationInLine, ProductImageInLine, ProductFileInLine]
    date_hierachy   = ['timestamp']
    list_display    = ['title', 'price', 'active', 'featured', 'is_digital']
    list_editable   = ['price', 'active', 'featured']
    #readonly_fields = ['updated', 'timestamp']

    class Meta:
        model = Product

admin.site.register(Product, ProductAdmin)


admin.site.register(Variation)


admin.site.register(ProductImage)

admin.site.register(ProductFile)