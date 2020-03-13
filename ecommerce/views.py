from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import ContactForm
from carts.models import Cart

def home_page(request):
    request.session['cart'] = False
    try:
        cart_obj = Cart.objects.get(id=request.session['cart_id'])
    except:
        cart_obj= None
    context = {
        'title': "Hello dudes",
        'content': "test me",
        'premium_content': "Supi Du hast Dich eingeloggt!",
        'cart': cart_obj,
    }
    return render(request, 'home-page.html', context)

def contact_page(request):
    request.session['cart'] = True
    form = ContactForm(request.POST or None)
    context = {
        'title': "Contact",
        'content': "Please send us a message here.",
        'form': form,
    }
    if form.is_valid():
        if request.is_ajax():
            return JsonResponse({"message": "Thank You for your submisssion!",})
    
    if form.errors:
        if request.is_ajax():
            errors = form.errors.as_json()            
            return HttpResponse(errors, status=400, content_type='application/json')
    
    return render(request, 'contact/view.html',context)

def about_page(request):
    request.session['cart'] = False
    context = {
        'title': "About this crap",
        'content': "brutal"
    }
    return render(request, 'base.html', context)

