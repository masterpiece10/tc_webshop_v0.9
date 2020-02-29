
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404, Http404


from .models import Product
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart



class ProductsFeaturedListView(ListView):
    queryset = Product.objects.all().featured()
    template_name = "list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductsFeaturedListView, self).get_context_data(*args, **kwargs)
        return context

class ProductFeaturedView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductFeaturedView, self).get_context_data(*args, **kwargs)

        return context

class UserProductsHistoryView(LoginRequiredMixin, ListView):
    template_name = "analytics/history.html"
  
    def get_context_data(self, *args, **kwargs):
        context = super(UserProductsHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
        return views 

class ProductsListView(ListView):
    queryset = Product.objects.all()
    template_name = "list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductsListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

class ProductDetailView(ObjectViewedMixin, DetailView):
    
    queryset = Product.objects.all()
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist!")

        return instance

class ProductDetailViewSlug(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailViewSlug, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        
        try:
            instance = get_object_or_404(Product, slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found ...")
        except Product.MultipleObjectsReturned:
            instance = Product.objects.get(slug=slug, avtive=True)
        except:
            return Http404("ahhhmm hmmmm")

        return instance
