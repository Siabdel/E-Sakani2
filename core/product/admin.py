from django.utils import timezone
from django.contrib import admin
from  mptt.admin  import MPTTModelAdmin
# Register your models here.
from core.product import models as pro_models 
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline


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


@admin.register(pro_models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display =  [field.name for field in pro_models.ProductImage._meta.get_fields()]

# Register your models here.
class ProductImageInline(StackedPolymorphicInline):
    model = pro_models.ProductImage
    readonly_fields = ('thumbnail_path', 'large_path',)

@admin.register(pro_models.Product)
class ProductAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    #base_model = car_models.VehiculeProduct 
    inlines = [ProductSpecificationValueInline, ProductImageInline, ]
    list_display =  [field.name for field in pro_models.Product._meta.get_fields()]
    prepopulated_fields = {'slug': ('name',), }
   