from django.urls import path

from .views import (
    cart_home,
    cart_update,
    checkout_home,
    checkout_done_view
    )

from billing.views import payment_method_view, payment_method_createview

urlpatterns = [
    
    path('', cart_home, name='home'),
    path('checkout/', checkout_home, name='checkout'),
    path('checkout/success/', checkout_done_view, name='success'),
    path('update/', cart_update, name='update'),
    path('payment/', payment_method_view, name='payment'),
    path('payment/create/', payment_method_createview, name='payment-create'),

    # path('<slug>/', ProductDetailViewSlug.as_view(), name='details'),
    
]