
# serializers.py
from rest_framework import serializers
from .models import Custom, Invoice, InvoiceItem

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom
        fields = '__all__'

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'

