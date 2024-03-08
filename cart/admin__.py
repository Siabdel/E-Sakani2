from django.contrib import admin
from immoshop import models as msh_models
from shop import models as sh_models

# Register your models here.

@admin.register(sh_models.ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_cart', 'created_at', 'statut', 'checked_out']
    
    def get_cart(self, obj):
        return obj.titre