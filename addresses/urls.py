from django.urls import path

from .views import (
    checkout_address_create_view, 
    checkout_address_reuse_view
    )

urlpatterns = [
    
    path('checkout/address/create_view/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse_view/', checkout_address_reuse_view, name='checkout_address_reuse'),

    
]