from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import CreateView, View, DetailView

from accounts.forms import ContactForm
from ads.models import Ads
from carts.models import Cart
from products.models import Product

import random

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

class ContactPage(View):
    def __init__(self):
        self.template_name = 'contact/view.html'

    def get(self, request, *args, **kwargs):
        request.session['cart'] = True
        form = ContactForm()
        context = {'form': form}
        prod_obj = Product.objects.featured()
        count = prod_obj.count()
        ads_obj = prod_obj[random.randint(0, count-1)] 
        ads_obj_db , created = Ads.objects.get_or_create(product = ads_obj)
        ads_obj_db.views += 1
        ads_obj_db.save()
        context["ads_obj"] = ads_obj 
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ContactForm(data=request.POST)
        if form.is_valid():
            self.send_mail(form.cleaned_data)
            form = ContactForm()
            return render(request, self.template_name , {'form': form})
        return render(request, self.template_name, {'form': form})

    def send_mail(self, valid_data):
        # Send mail logic
        print(valid_data)
        pass

    def get_context_data(self, **kwargs):
        context = super(ContactPage).get_context_data(**kwargs)
        
        return context
    

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

    def get_context_data(self, **kwargs):
        context = super(contact_page, request).get_context_data(**kwargs)
        context["contact"] = "something"
        return context
    

def about_page(request):
    request.session['cart'] = False
    context = {
        'title': "About",
        'content': "Here will be the about information"
    }
    return render(request, 'base.html', context)

