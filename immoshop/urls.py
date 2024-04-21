from django.urls import path
from core.shop import views 
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from weasyprint import HTML


app_name="immoshop"

urlpatterns = [
    #path('home/', views.product_immo_list, name='home_immo_list'),
    path('', views.product_home, name='home_immo_list'),
    path('home/', views.product_home, name='home_immo_list'),
    path('list/', views.product_home, name='product_immo_list'),
    path('cat/<slug:category_slug>/', views.product_immo_list, name='product_list_by_category'),
    path('show/<int:pk>/', views.ProductDetailView.as_view(), name='product_immo_detail'),
    path( "invoices/generate/<invoice_id>", views.generate_pdf_invoice, name="generate_pdf",),
]