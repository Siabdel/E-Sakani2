from django.urls import path
from core.shop import views as shop_models 
from immoshop import views as immo_models
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
    ## path('add_account/', immo_models.AccountCreate.as_view(), name='account_create'),
    # path('create_account/', immo_models.AccompteUserCreate.as_view(), name='account_create'),
    path('create_account/', immo_models.CreateAccount.as_view(), name='account_create'),
    #
    path('create_invoice/<int:user_id>', immo_models.InvoiceCreate.as_view(), name='invoice_create'),
    path('invoices/generate/<int:invoice_id>', immo_models.generate_pdf_invoice, name="generate_pdf",),
]