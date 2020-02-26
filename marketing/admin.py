from django.contrib import admin

from .models import MarketingPreference

class MarketingPreferencesAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'active', 'subscribed', 'mailchimp_subscribed', 'code_400']
    list_filter = ['active', 'subscribed', 'mailchimp_subscribed', 'code_400']
    search_fields = ['email']
    readonly_fields = ['mailchimp_subscribed', 'updated', 'timestamp', 'mailchimp_msg']
    class Meta:
        model = MarketingPreference
        fields = [
            'user',
            'active', 
            'subscribed',
            'mailchimp_msg',
            'mailchimp_subscribed',
            'timestamp',
            'updated',            
        ]

admin.site.register(MarketingPreference, MarketingPreferencesAdmin)
