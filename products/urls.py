from django.urls import path, re_path

from .views import (
    ProductsListView, 
    ProductDetailViewSlug,
    ProductDownloadView
    )

urlpatterns = [
    
    path('', ProductsListView.as_view(), name='products'), 
    re_path(r'^(?P<slug>[\w-]+)/(?P<pk>\d+)/$', ProductDownloadView.as_view(), name='download'),
    re_path(r'^(?P<slug>[\w-]+)/$', ProductDetailViewSlug.as_view(), name='details'),
   
    
]