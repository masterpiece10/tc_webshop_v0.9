from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Cart
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.models import Address
from addresses.forms import AddressForm
from billing.models import BillingProfile
from orders.models import Order
from products.models import Product

STRIPE_PUBLISH = settings.STRIPE_LIVE_PUBLIC_KEY or None

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        "id": x.id,
        "url": x.get_absolute_url(),
        "name": x.name, 
        "price": x.price
        } 
        for x in cart_obj.product.all()]
    context = {
            "products": products,
            "subtotal": cart_obj.subtotal,
            "total": cart_obj.total,
    }
    return JsonResponse(context)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {'cart': cart_obj,}
    template = "carts/home.html"

    return render(request,template , context)

def cart_update(request):
    product_id = request.POST.get('product_id')
    if product_id: # is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("sorry product is not available")
            return redirect("carts:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj not in cart_obj.product.all():
            cart_obj.product.add(product_obj)
            added = True
        else:
            cart_obj.product.remove(product_obj)
            added = False
        request.session['cart_items'] = cart_obj.product.count()
        # return redirect(product_obj.get_absolute_url())
        if request.is_ajax():
            jason_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_obj.product.count(),
            }
            return JsonResponse(jason_data)
    return redirect("carts:home")

def checkout_home(request):
    
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.product.count() == 0:
        return redirect("carts:home")
   
    billing_profile = None
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressForm()
    billing_address_id = request.session.get('billing_address_id', None)

    shipping_address_required = not cart_obj.is_digital

    shipping_address_id = request.session.get('shipping_address_id', None)

        
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            #
            # get billing profile for reusable addresses
            #
            address_qs = Address.objects.filter(billing_profile=billing_profile)
            #
            #
            #
        order_obj, created = Order.objects.new_or_get(billing_profile, cart_obj )
        if shipping_address_id is not None:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id is not None:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if billing_address_id or shipping_address_id:
            order_obj.save()
        
        has_card = billing_profile.has_card

        if request.method == "POST":
            is_prepared = order_obj.check_done()
            if is_prepared:
                did_charge, crg_msg = billing_profile.charge(order_obj)
                if did_charge:
                    order_obj.mark_paid()
                    request.session['cart_items'] = 0
                    del request.session['cart_id']
                    if not billing_profile.user:
                        billing_profile.set_cards_inactive()
                    return redirect("carts:success")
                else:
                    return redirect("carts:checkout")
    
    context = {
        'object': order_obj,
        'billing_profile': billing_profile,
        'login_form': login_form,
        'guest_form': guest_form,
        'address_form': address_form,
        'address_qs': address_qs,
        'has_card': has_card,
        'publishable_key': STRIPE_PUBLISH,
        'shipping_address_required': shipping_address_required,
    }
    template = 'carts/checkout.html'
    return render(request, template, context)

def checkout_done_view(request):
    context = {}
    template = 'carts/checkout-done.html'
    return render(request, template, context)