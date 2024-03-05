from django.urls import path
from immoshop import views 

app_name="immoshop"

urlpatterns = [
    path('home/', views.product_immo_list, name='home_immo_list'),
    path('list/', views.product_immo_list, name='product_immo_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_immo_detail'),
]