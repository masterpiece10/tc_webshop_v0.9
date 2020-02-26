from django.urls import path
from .views import SearchProductView

urlpatterns = [
    
    path('', SearchProductView.as_view(), name='query'),
    # path('<slug>/', ProductDetailViewSlug.as_view(), name='details'),
    
]