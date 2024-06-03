import os
import tempfile
from django.contrib import admin
from core.shop import models as sh_models

class ItemArticleAdmin(admin.ModelAdmin):
    #list_display =  [field.name for field in sh_models.ItemArticle._meta.get_fields()]
    list_display =  ['content_object', ]



admin.register(sh_models.ItemArticle)