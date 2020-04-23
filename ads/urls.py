from django.urls import path

from .views import index
from analytics.views import AdsStatisticsView

urlpatterns = [
    path('', index),
    path('analytics/', AdsStatisticsView.as_view(), name="ads-statistics"),
]
