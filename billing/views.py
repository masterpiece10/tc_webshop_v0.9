from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url
from django.views.generic import View

from .models import BillingProfile, Card
from carts.models import Cart, CartItem
from orders.models import Order
from ecommerce.utils import render_to_pdf

import datetime
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

def invoices(request):
    if request.user.is_authenticated:
        template_name = 'billing/invoices.html'
        context = {"title": f"Invoices for {request.user}",}
        billing_profile = BillingProfile.objects.get(user=request.user)
        order_objs = Order.objects.filter(billing_profile = billing_profile).filter(status = 'paid')
        context['invoices'] = order_objs

    else:
        return redirect('login')
    return render(request, template_name, context)

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        slug = None
        if request.GET:
            slug = request.GET.get('slug')
        data = {
            'today': datetime.date.today(), 
            'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'slug': slug,
        }
        order_obj = Order.objects.get(order_id = slug) or None
        cart_item_obj = CartItem.objects.all().filter(cart = order_obj.cart)
        if order_obj is not None:
            data['items'] = cart_item_obj
            data['order'] = order_obj
        else:
            data['items'] = None
            data['order'] = None
        filename = slug
        pdf = render_to_pdf('pdf/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')