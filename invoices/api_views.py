
# views.py
from rest_framework import generics
from .models import Custom, Invoice, InvoiceItem
from .serializers import ClientSerializer, InvoiceSerializer, InvoiceItemSerializer

class ClientListView(generics.ListCreateAPIView):
    queryset = Custom.objects.all()
    serializer_class = ClientSerializer

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Custom.objects.all()
    serializer_class = ClientSerializer

class InvoiceListView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class InvoiceItemListView(generics.ListCreateAPIView):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer

class InvoiceItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
