from django.urls import path, re_path

from .views import (
    ProductsListView, 
    ProductDetailViewSlug,
    ProductDownloadView,
    ProductDetailViewAdd,
    )

urlpatterns = [
    
    path('', ProductsListView.as_view(), name='products'), 
    re_path(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)/$', ProductDownloadView.as_view(), name='download'),
    re_path(r'^(?P<slug>[\w-]+)/$', ProductDetailViewSlug.as_view(), name='details'),
    re_path(r'^(?P<slug>[\w-]+)/add/', ProductDetailViewAdd.as_view(), name='add-to-ads-view'),
   
    
]