from django.urls import path
from shop import views 

app_name="shop"

urlpatterns = [
    #path('cat/<slug:category_slug>/', views.product_shop_list, name='product_list_by_category'),
    path('show/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('add/<int:product_id>/', views.cart_add_one_item, name='cart_add_item'),
]