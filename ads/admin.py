from django.contrib import admin

from .models import Ads

# Register your models here.

class AdsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'date_started', 'date_ended', 'views', 'clicks']
    list_filter = ['clicks', 'views']
    # search_fields = ['__str__']
    # readonly_fields = ['views', 'clicks',  'updated', 'timestamp']
    class Meta:
        model = Ads
        fields = [
            'user',
            'active', 
            'subscribed',
            'mailchimp_msg',
            'mailchimp_subscribed',
            'timestamp',
            'updated',            
        ]

admin.site.register(Ads, AdsAdmin)
