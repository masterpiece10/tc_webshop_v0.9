from django.core import serializers
from django.http.response import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, Http404, redirect



# Create your views here.

from products.models import Product

class SearchProductView(ListView):
    queryset = Product.objects.all()
    template_name = "search/list.html"
    

    # def get_context_data(self, *args, **kwargs):
    #     context = super(SearchProductView, self).get_context_data(*args, **kwargs)
    #     return context

    def get_queryset(self, *args, **kwargs):
        self.request.session['cart'] = False
        request = self.request
        method_dict = request.GET
        q = request.GET.get('q', None)
        if q is not None:
            return Product.objects.search(q)
        return Product.objects.none()

def fluid_search(request):
    template_name = "search/list.html"
    q= None
    print(request.is_ajax)
    if request.is_ajax:
        if request.GET:
            q= request.GET.get('p')
        elif request.POST:
            q = request.POST.get('q')\
            
        if q is None:
            qs = Product.objects.all()
            json_qs = serializers.serialize('json', qs)
            return HttpResponse(json_qs, content_type='application/json', status=200)
        else:
            qs = Product.objects.search(q)
            context = {"object_list": qs,}
            return render(request, template_name, context)
    else:
        json_qs = {}
    return redirect('home')
