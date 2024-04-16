from django.utils import timezone
from django.contrib import admin
from  mptt.admin  import MPTTModelAdmin
# Register your models here.
from core.product import models as pro_models 

class ProductSpecificationInline(admin.TabularInline):
    model = pro_models.ProductSpecification


class ProductSpecificationValueInline(admin.TabularInline):
    model = pro_models.ProductSpecificationValue
    
@admin.register(pro_models.ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductSpecificationInline, ]

@admin.register(pro_models.ProductSpecificationValue)
class ProductSpecificationValue(admin.ModelAdmin):
    list_display =  [field.name for field in pro_models.ProductSpecificationValue._meta.get_fields()]

    
@admin.register(pro_models.MPCategory)
class ProductCategoyAdmin(MPTTModelAdmin):
    list_display = ["name", "name",]
    prepopulated_fields = {'slug': ('name',), }

