
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404, Http404, HttpResponse, redirect


from .models import Product, ProductFile
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart, CartItem
from orders.models import ProductPurchase,Order

import os
from mimetypes import guess_type, guess_extension
from wsgiref.util import FileWrapper

class ProductsFeaturedListView(ListView):
    queryset = Product.objects.all().featured()
    template_name = "list.html"

    def get_context_data(self, *args, **kwargs):
        self.request.session['cart'] = False
        context = super(ProductsFeaturedListView, self).get_context_data(*args, **kwargs)
        return context

class ProductFeaturedView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        self.request.session['cart'] = False
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
        self.request.session['cart'] = False
        prod_qs = Product.objects.all()
        context = super(ProductsListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        
        # cart_item_object, new_cart_item = CartItem.objects.filter(cart=cart_obj)
        in_cart = []
        for product in prod_qs:
            for item in cart_obj.cartitem_set.all():
                if product == item.product:
                    in_cart.append(product)
        
        context['cart'] = cart_obj
        context['in_cart'] = in_cart
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()

class ProductDetailViewSlug(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        self.request.session['cart'] = False
        user = self.request.user
        context = super(ProductDetailViewSlug, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        product_obj = context['product']
        if user.is_authenticated:
            if product_obj.is_digital:
                purchased_qs = ProductPurchase.objects.by_request(self.request)
                order_qs =  Order.objects.by_request(self.request).not_created()
                order = order_qs.first()
                purchased = purchased_qs.first()
                try:
                    purchase_date = purchased.timestamp
                    context['date_purchased'] = purchase_date
                except:
                    pass
            
            
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        
        try:
            instance = get_object_or_404(Product, slug=slug, active=True)
        except Product.DoesNotExist:
            messages.error(request, "Product not found. Please chose something else.")
            raise Http404("Product not found")
        except Product.MultipleObjectsReturned:
            instance = Product.objects.get(slug=slug, avtive=True)
        except:
            return Http404("ahhhmm hmmmm")

        return instance



class ProductDownloadView(View):
    def get(self, request, *args, **kwargs):
        self.request.session['cart'] = False
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        can_download = False
        user_ready = True


        purchased_products = Product.objects.none()
        downloads_qs = ProductFile.objects.filter(pk=pk, product__slug=slug) 
        if downloads_qs.count() != 1:
            raise Http404('Download not found')
        downloads_obj = downloads_qs.first()

        if downloads_obj.user_required: 
            if request.user.is_authenticated:
                user_ready = False
                
        
        if downloads_obj.free:
            can_download = True
           
        else:
            purchased_products = ProductPurchase.objects.products_by_request(request)
            if downloads_obj.product in purchased_products:
                can_download = True
        if not can_download or not user_ready:
            messages.error(request, "You do not have access to download this item.")
            return redirect(downloads_obj.get_default_url())
        


        file_root = settings.PROTECTED_ROOT
        filepath = downloads_obj.file.path
        final_filepath = os.path.join(file_root, filepath)
        with open(final_filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mimetype = "application/force-download"
            guessed_mimetype = guess_type(filepath)[0]
            if guessed_mimetype:
                mimetype = guessed_mimetype
                extention = os.path.splitext(filepath)[1]
            response =  HttpResponse(wrapper, content_type=mimetype)
            response['Content-Disposition'] = f"attachement;filename={downloads_obj.display_name}.{extention}"
            response['X-SendFile'] = str(downloads_obj.name)
            return response
