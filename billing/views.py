from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import BillingProfile, Card

import stripe

stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
STRIPE_LIVE_PUBLIC_KEY = settings.STRIPE_LIVE_PUBLIC_KEY



def payment_method_view(request):
    request.session['cart'] = True
    # if request.user.is_authenticated:
    #     billing_profile = request.user.billingprofile
    #     my_customer_id = billing_profile.customer_id
        
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
            return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_    
    return render(request, 'billing/payment-method.html', {'publishable_key': STRIPE_LIVE_PUBLIC_KEY, "next_url": next_url})

def payment_method_createview(request):
    current_page = request.META.get('HTTP_REFERER')
    request.session['cart'] = True
    if request.method == "POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            messages.error(request, "User not found. Please login.")
            return HttpResponse({"message", "Cannot find this user."}, status=401)
        token = request.POST.get("token")
        if token is not None:
            new_car_obj = Card.objects.add_new(billing_profile, token)
        messages.success(request, "Payment method was successfully added!")
        return JsonResponse({'message': "Success! Your Card was added."})
    
    return render(request, "401.html", status=401)

