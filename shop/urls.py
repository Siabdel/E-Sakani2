from django.urls import path
from shop import views 

app_name="shop"

urlpatterns = [
    #path('home/', views.product_shop_list, name='home_shop_list'),
    path('home/', views.product_shop_home, name='home_shop_list'),
    path('list/', views.product_shop_home, name='product_shop_list'),
    path('cat/<slug:category_slug>/', views.product_shop_list, name='product_list_by_category'),
    path('show/<int:pk>/', views.ProductDetailView.as_view(), name='product_shop_detail'),
]