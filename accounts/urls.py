from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView 
from .views import (
                RegisterView, 
                logout_page, 
                LoginView, 
                AccountHomeVIew, 
                AccountEmailActivateView, 
                GuestRegisterView,
                UserDetailUpdateView,
                )
from products.views import UserProductsHistoryView

urlpatterns = [
    path('guest_register/',GuestRegisterView.as_view(), name='guest_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('history/products/', UserProductsHistoryView.as_view(), name='user-product-history'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', AccountHomeVIew.as_view(), name='home'),
    path('details/', UserDetailUpdateView.as_view(), name='user-update'),
    path('email/confirm/<key>/', AccountEmailActivateView.as_view(), name='email-activate'),
    path('email/resend-activation/', AccountEmailActivateView.as_view(), name='resend-activation'),


]