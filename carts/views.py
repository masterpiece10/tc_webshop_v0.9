from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect

from .models import Cart, CartItem
from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.models import Address
from addresses.forms import AddressForm
from billing.models import BillingProfile
from orders.models import Order
from products.models import Product, Variation

STRIPE_PUBLISH = settings.STRIPE_LIVE_PUBLIC_KEY or None

def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
        "id": x.product.id,
        "name": x.product.name, 
        "price": x.product.price,
        "quantity": x.quantity,
        } 
        for x in cart_obj.cartitem_set.all()]
    context = {
            "products": products,
            "subtotal": cart_obj.subtotal,
            "total": cart_obj.total,
    }
    return JsonResponse(context)

def cart_home(request):
    request.session['cart'] = True
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {'cart': cart_obj,}
    template = "carts/home.html"

    return render(request, template, context)




def cart_update(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        cart_item = request.POST.get('cartitemId') or None
        qty = request.POST.get('qty') or None
        notes = {}
        product_var = []
        current_page = request.META.get('HTTP_REFERER')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        request.session['cart_id'] = cart_obj.id
        
        try:
            color = request.POST.get('color')
            v = Variation.objects.get(id=color)
            product_var.append(v)
        except:
            pass
        try:
            size = request.POST.get('size')
            v = Variation.objects.get(id=size)
            product_var.append(v)
        except:
            pass
        if int(qty) == 0:
                        cart_item_product = CartItem.objects.filter(id=cart_item)
                        if cart_item is not None:
                            item_delted = cart_item_product.first().product or ""
                        else:
                            cart_item_product = ""
                        if cart_item_product != "":
                            messages.success(request, f"Product <strong>{item_delted}</strong> was successfully deleted.")
                            cart_item_product.delete()
                            cart_obj.save()
                        else:
                            return redirect(current_page)
        if product_id: # is not None:
            try:
                product_obj = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                messages.error(request, "Product is momentarely not available. Please try again later.")
                return redirect("carts:home")
            
            cart_item_obj = CartItem.objects.create(cart=cart_obj, product=product_obj)
                        
            if int(qty) > 0:
                if len(product_var) > 0:
                    cart_item_obj.variation.clear()
                    cart_item_obj.variation.add(*product_var)
                cart_item_obj.quantity = qty
                cart_item_obj.notes = notes
                cart_item_obj.save()
                added = True
                messages.info(request, f"Product <strong>{cart_item_obj.product.title}</strong> was successfully added.")

                cart_obj.save() # called to update the total and subtotal prices
          
            if request.is_ajax():
                jason_data = {
                    "added": added,
                    "removed": not added,
                    "cartItemCount": cart_obj.cartitem_set.all().count(),
                }
                return JsonResponse(jason_data)
        request.session['cart_items'] = cart_obj.cartitem_set.all().count()
        if request.session['cart_items'] <= 0:
            return redirect('/products/')
    return redirect(current_page)

def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.cartitem_set.all().count() == 0:
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
        'cart': cart_obj,
    }
    template = 'carts/checkout.html'
    return render(request, template, context)

def checkout_done_view(request):
    context = {}
    template = 'carts/checkout-done.html'
    return render(request, template, context)

