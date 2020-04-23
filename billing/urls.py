from django.urls import path

from .views import invoices, GeneratePdf

urlpatterns = [
    path('invoices/', invoices, name="invoices"),
    path('invoices/get_pdf', GeneratePdf.as_view(), name='get_pdf' ),
]
