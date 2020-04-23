from django.shortcuts import render
from django.template.response import TemplateResponse

# Create your views here.

def index(request):
    request.session['cart'] = True
    context = {
        "title": "Ads Master Page"
    }
    return TemplateResponse(request, 'ads/index.html', context)