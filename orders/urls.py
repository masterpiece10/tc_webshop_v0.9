from django.urls import path, include

from .views import (
                OrderDetailView,
                OrderListView,
                VerifyOwbership
                )
from products.views import UserProductsHistoryView

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('endpoint/verify/ownership', VerifyOwbership.as_view(), name='verify-ownership'),
    path('<order_id>/', OrderDetailView.as_view(), name='detail'),

]