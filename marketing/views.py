from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import UpdateView, View
from django.shortcuts import render, redirect

# Create your views here.

from .forms import MarketingPreferenceForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp

MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)

if MAILCHIMP_EMAIL_LIST_ID is None:
    raise NotImplementedError("MAILCHIMP_EMAIL_LIST_ID must be set in the settings, something like us17")

class MailchimpWebhookView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            email = data.get('data[email]')
            hook_type = data.get("type")
            response_status, response = Mailchimp().check_subscription_status(email)
            sub_status = response['status']
            is_subbed = None
            mailchimp_subbed = None
            if sub_status == 'subscribed':
                mailchimp_subbed, is_subbed = (True, True)
            elif sub_status == 'unsubscribed':
                mailchimp_subbed, is_subbed = (False, False)
            if is_subbed is not None and mailchimp_subbed is not None:    
                qs = MarketingPreference.objects.filter(user__email__iexact=email)
                if qs.exists():
                    qs.update(
                        subscribed=is_subbed, 
                        ailchimp_subscribed=mailchimp_subbed, 
                        mailchimp_msg=str(data),
                        )
        return HttpResponse("Thank you", status=200)

class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name =  'base/forms.html'
    success_url = '/settings/email/'
    success_message = 'Your eMail Prefereces have been updated. Thank You.'
    
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return redirect("/accounts/login/?next=/settings/email/")
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView, self).get_context_data(*args, **kwargs)
        context["title"] = "Marketing Email Preferences"
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(user=user)
        return obj
    
    def get_success_message(self, cleaned_data):
        return self.success_message 

# def mailchimp_webhook_view(request):
#     data = request.POST
#     list_id = data.get('data[list_id]')
#     if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
#         email = data.get('data[email]')
#         hook_type = data.get("type")
#         response_status, response = Mailchimp().check_subscription_status(email)
#         sub_status = response['status']
#         is_subbed = None
#         mailchimp_subbed = None
#         if sub_status == 'subscribed':
#             mailchimp_subbed, is_subbed = (True, True)
#         elif sub_status == 'unsubscribed':
#             mailchimp_subbed, is_subbed = (False, False)
#         if is_subbed is not None and mailchimp_subbed is not None:    
#             qs = MarketingPreference.objects.filter(user__email__iexact=email)
#             if qs.exists():
#                 qs.update(
#                     subscribed=is_subbed, 
#                     ailchimp_subscribed=mailchimp_subbed, 
#                     mailchimp_msg=str(data),
#                     )


#     return HttpResponse("Thank you", status=200)