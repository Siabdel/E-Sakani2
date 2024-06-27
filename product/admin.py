import os
from django.utils import timezone
from django.contrib import admin
from  mptt.admin  import MPTTModelAdmin
# Register your models here.
from product import models as pro_models 
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from django.contrib.admin import StackedInline
from django.conf import settings
from core import utils as sh_utils

class ProductSpecificationInline(admin.TabularInline):
    model = pro_models.ProductSpecification


class ProductSpecificationValueInline(admin.TabularInline):
    model = pro_models.ProductSpecificationValue
    
@admin.register(pro_models.ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductSpecificationInline, ]

class ProductSpecificationValueInline(admin.TabularInline):
    model = pro_models.ProductSpecificationValue
    extra = 0
    
@admin.register(pro_models.ProductSpecificationValue)
class ProductSpecificationValue(admin.ModelAdmin):
    #list_display =  [field.name for field in pro_models.ProductSpecificationValue._meta.get_fields()]
    list_display = ('product', 'specification', 'value',) 

    
@admin.register(pro_models.MPCategory)
class ProductCategoyAdmin(MPTTModelAdmin):
    list_display = ["name", "name",]
    prepopulated_fields = {'slug': ('name',), }


@admin.register(pro_models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display =  [field.name for field in pro_models.ProductImage._meta.get_fields()]

# Register your models here.
class ProductImageInline(StackedInline):
    model = pro_models.ProductImage
    readonly_fields = ('thumbnail_path', 'large_path',)
    fields = ('title', 'image',  )
    extra = 0

@admin.register(pro_models.Product)
class ProductAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    #base_model = car_models.VehiculeProduct 
    inlines = [ProductSpecificationValueInline, ProductImageInline, ]
    #list_display =  [field.name for field in pro_models.Product._meta.get_fields()]
    list_display = ['name', 'project', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    # readonly_fields = ('thumbnail_path', 'large_path',  )
    exlude = ('thumbnail_path', 'large_path',  )
    search_fields = ["name", "slug", ]
    
    fieldsets = (
        (
            "Required Information", {
                # Section Description
                "description" : "Enter the Project information",
                # Group Make and Model
                "fields": (("project", "name"), "slug", "product_code", "description", )
            }, 
        ),
        
        (
            "Required Information 2", {
                "fields": ("stock", "price", "regular_price", "discount_price", )
            },
        ),
        (
            "Additional Information", {
                # Section Description
                #Enable a Collapsible Section
                "classes": ("collapse",), 
                "fields": ("in_stock", "is_active", "default_image")
            }
        )
    )
    
   

    def save_model(self, request, obj, form, change):
        """
        Custom save method to process images when saving a Product instance.
        """
        super().save_model(request, obj, form, change)
        self.save_form(request, form, change)
        output_dir = os.path.join(settings.MEDIA_ROOT, "images")
        # Check if there are any images associated with this product
        if obj.images.exists():
            # Process each image associated with the product
            for image in obj.images.all():
                # processus de resize images
                thumbnail_path, large_path = sh_utils.process_resize_image(image, output_dir)
                # You can save these paths to the database if needed
                image.large_path = os.path.join("media/images/", os.path.basename(large_path))
                image.thumbnail_path = os.path.join("media/images/", os.path.basename(thumbnail_path))
                image.save() 

    def save_related(self, request, form, formsets, change):
        output_dir = os.path.join(settings.MEDIA_ROOT, "images")
        super().save_related(request, form, formsets, change)

        
        # Accéder à l'instance de Product nouvellement sauvegardée
        product_instance = form.instance
       
        # Modifier les objets ProductImage associés
        for product_image in product_instance.images.all():
            # processus de resize images
            thumbnail_path, large_path = sh_utils.process_resize_image(product_image, output_dir)
            # Faire des modifications sur les objets ProductImage thumbnail_path, large_path = sh_utils.process_resize_image(new_image, output_dir)


            product_image.large_path = os.path.join("/media/images/", os.path.basename(large_path))
            product_image.thumbnail_path = os.path.join("/media/images/", os.path.basename(thumbnail_path))
            product_image.save()
