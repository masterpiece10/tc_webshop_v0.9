from django.urls import path

from .views import (
    ProductsListView, 
    ProductDetailView,
    ProductFeaturedView,
    ProductsFeaturedListView,
    ProductDetailViewSlug,
    )

urlpatterns = [
    
    path('', ProductsListView.as_view(), name='products'),
    path('<slug>/', ProductDetailViewSlug.as_view(), name='details'),
    
]