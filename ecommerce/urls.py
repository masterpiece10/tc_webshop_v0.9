"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

from .views import home_page, contact_page, about_page
from accounts.views import LoginView, RegisterView
from billing.views import payment_method_createview, payment_method_view
from carts.views import cart_detail_api_view
from marketing.views import MarketingPreferenceUpdateView, MailchimpWebhookView
from orders.views import LibraryView
from products.views import ProductDetailViewSlug







urlpatterns = [
    
    path('', home_page, name='home'),
    path('accounts/', include (('accounts.passwords.urls', 'change'))),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('accounts/', RedirectView.as_view(url="/account/")),
    path('api/cart/', cart_detail_api_view, name='api-cart'),
    path('contact/', contact_page, name='contact'),
    path('about/', about_page, name='about'),
    path('library/', LibraryView.as_view(), name='library'),
    path('payment/', payment_method_view, name='payment'),
    path('payment/create/', payment_method_createview, name='payment-create'),
    path('admin/', admin.site.urls),
    path('products/', include (('products.urls', 'products' ))),
    path('settings/email/', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    path('settings/', RedirectView.as_view(url="/accounts")),
    path('webhooks/mailchimp/', MarketingPreferenceUpdateView.as_view(), name='webhooks-mailchimp'),
    path('search/', include (('search.urls', 'search' ))),
    path('cart/', include (('carts.urls', 'carts' ))), 
   
    path('account/', include (('accounts.urls', 'accounts' ))),
    path('addresses/', include (('addresses.urls', 'addresses' ))),
    path('orders/', include (('orders.urls', 'orders' ))),
   
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)