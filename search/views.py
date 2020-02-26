from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, Http404


# Create your views here.

from products.models import Product

class SearchProductView(ListView):
    queryset = Product.objects.all()
    template_name = "search/list.html"
    

    # def get_context_data(self, *args, **kwargs):
    #     context = super(SearchProductView, self).get_context_data(*args, **kwargs)
    #     return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        q = request.GET.get('q', None)
        if q is not None:
            return Product.objects.search(q)
        return Product.objects.none()