from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from .utils import Mailchimp

# Create your models here.

class MarketingPreference(models.Model):
    user                    = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    email                   = models.CharField(max_length=255, null=True, blank=True)
    subscribed              = models.BooleanField(default=True)
    mailchimp_subscribed    = models.NullBooleanField(blank=True)
    active                  = models.BooleanField(default=True)
    mailchimp_msg           = models.TextField(null=True, blank=True)
    timestamp               = models.DateTimeField(auto_now_add=True)
    updated                 = models.DateTimeField(auto_now=True)
    code_400                = models.NullBooleanField(blank=True, default=False)
    code_400_text           = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.email:
            return "email: " + self.email
        else:
            return self.user.email

def marketing_pref_update_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().add_email(instance.user.email)
        

post_save.connect(marketing_pref_update_receiver, sender=MarketingPreference)

def make_marketing_create_receiver(sender, instance, created, *args, **kwargs):
    """
    User model
    """
    if created:
        MarketingPreference.objects.get_or_create(user=instance)
        marketing_obj = MarketingPreference.objects.get(user=instance)
        marketing_obj.email = instance.email
        marketing_obj.code_400 = False
        marketing_obj.save()



post_save.connect(make_marketing_create_receiver, sender=settings.AUTH_USER_MODEL)

def marketing_pref_update_receiver(sender, instance, *args, **kwargs):
    if instance.active == False:
        pass
    else:
        status_code, response_data = Mailchimp().add_email(instance.user.email)
        if status_code == 400 and "permanently deleted" in response_data['detail']:
            status_code, response_data = Mailchimp().code_400_subscribe(instance.user.email)
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.code_400 = True
            instance.code_400_text = response_data['detail']
            instance.mailchimp_msg = response_data
            instance.active = False
        else:
            if instance.subscribed != instance.mailchimp_subscribed:
                if instance.subscribed:
                    # subscribing
                    status_code, response_data = Mailchimp().subscribe(instance.user.email)
                else:
                    # unsubsribing
                    status_code, response_data = Mailchimp().unsubscribe(instance.user.email)
                
                if response_data['status'] == 'subscribed':
                    instance.subscribed = True
                    instance.mailchimp_subscribed = True
                    instance.mailchimp_msg = response_data
                else:
                    instance.subscribed = False
                    instance.mailchimp_subscribed = False
                    instance.mailchimp_msg = response_data

pre_save.connect(marketing_pref_update_receiver, sender=MarketingPreference)