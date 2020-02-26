from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from accounts.forms import ContactForm

def home_page(request):
    context = {
        'title': "Hello dudes",
        'content': "test me",
        'premium_content': "Supi Du hast Dich eingeloggt!",
    }
    return render(request, 'home-page.html', context)

def contact_page(request):
    form = ContactForm(request.POST or None)
    context = {
        'title': "Contact",
        'content': "here you can contact me",
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
    context = {
        'title': "About this crap",
        'content': "brutal"
    }
    return render(request, 'base.html', context)

