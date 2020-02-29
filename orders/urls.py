from django.urls import path, include

from .views import (
                OrderDetailView,
                OrderListView
                )
from products.views import UserProductsHistoryView

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('<order_id>/', OrderDetailView.as_view(), name='detail'),

]