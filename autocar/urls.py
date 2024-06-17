from django.urls import path
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from weasyprint import HTML
from core.shop import views as shop_models 


app_name="carshop"

urlpatterns = [
    path('show/<int:pk>/', shop_models.ProductDetailView.as_view(), name='product_car_detail'),
]