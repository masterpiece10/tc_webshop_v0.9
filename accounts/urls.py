from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView 
from .views import RegisterView, guest_register_page, logout_page, LoginView
urlpatterns = [
    path('guest_register/', guest_register_page, name='guest_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),


]