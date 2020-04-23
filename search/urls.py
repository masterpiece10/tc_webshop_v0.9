from django.urls import path
from .views import (
    SearchProductView,
    fluid_search,
)

urlpatterns = [
    
    path('', SearchProductView.as_view(), name='query'),
    path('ajax-search/', fluid_search, name='fluid-search')
    # path('<slug>/', ProductDetailViewSlug.as_view(), name='details'),
    
]