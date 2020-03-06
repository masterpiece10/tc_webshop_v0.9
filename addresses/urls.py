from django.urls import path

from .views import (
    checkout_address_create_view, 
    checkout_address_reuse_view,
    AddressUpdateView,
    AddressListView,
    AddressCreateView,
    )

urlpatterns = [

    path('', AddressListView.as_view(), name='home'),
    path('checkout/address/create_view/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse_view/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('address/change/<pk>', AddressUpdateView.as_view(), name='address-change'),
    path('create/', AddressCreateView.as_view(), name='address-create'),
    

    
]