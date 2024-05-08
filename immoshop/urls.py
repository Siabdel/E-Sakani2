from django.urls import path
from core.shop import views as shop_models 
from immoshop import views as immo_views
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
    #path('home/', shop_models.product_immo_list, name='home_immo_list'),
    path('', shop_models.product_home, name='home_immo_list'),
    path('home/', shop_models.product_home, name='home_immo_list'),
    path('list/', shop_models.product_home, name='product_immo_list'),
    path('cat/<slug:category_slug>/', shop_models.product_immo_list, name='product_list_by_category'),
    path('show/<int:pk>/', shop_models.ProductDetailView.as_view(), name='product_immo_detail'),
    ## Devis 
    path('create_user/', immo_views.UserCreate.as_view(), name='user_create'),
    ## path('create_account/', immo_views.CreateAccount.as_view(), name='account_create'),
    path('add_client/', immo_views.CustomCreate.as_view(), name='client_create'),
    #
    path('create_invoice/<int:user_id>', immo_views.InvoiceCreate.as_view(), name='invoice_create'),
    path('invoices/generate/<int:invoice_id>', immo_views.generate_pdf_invoice, name="generate_pdf",),
    ## 
    path('success/', immo_views.success, name="success",),
]