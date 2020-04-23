from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, View

from .models import Order, ProductPurchase
from billing.models import BillingProfile

class OrderListView(LoginRequiredMixin, ListView):
    
    def get_queryset(self):
        self.request.session['cart'] = False
        qs = Order.objects.by_request(self.request).not_created()
        return qs

class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'
    
    
    def get_queryset(self):
        self.request.session['cart'] = False
        qs = ProductPurchase.objects.products_by_request(self.request) # by_request(self.request).digital()
        
        return qs

class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/details.html'

    def get_object(self):
        self.request.session['cart'] = False
        qs = Order.objects.by_request(self.request)\
                    .filter(
                    order_id = self.kwargs.get('order_id')
                )
        if qs.count() == 1:
            return qs.first()
        return Http404


class VerifyOwbership(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.request.session['cart'] = False
        if request.is_ajax:
            data = request.GET
            product_id = data.get('product_id')
            if product_id is not None:
                product_id = int(product_id)
                ownership_ids = ProductPurchase.objects.products_by_id(request)
                if product_id in ownership_ids:
                    return JsonResponse({"owner": True})
                return JsonResponse({"owner": False})
        return Http404('nothing')