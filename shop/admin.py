import os
import tempfile
from django.contrib import admin
from shop import models as sh_models

@admin.register(sh_models.ShopCart)
class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_cart', 'created_at', 'statut', 'checked_out']
    
    def get_cart(self, obj):
        return obj.titre


@admin.register(sh_models.ItemArticle)
class ItemArticleAdmin(admin.ModelAdmin):
    #list_display =  [field.name for field in sh_models.ItemArticle._meta.get_fields()]
    list_display =  ['product', ]