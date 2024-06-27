from django.urls import path
from . import views 

app_name = 'customer'

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    ## Create
    path('create_account/', views.CustomCreate.as_view(), name='account_create'),
]


