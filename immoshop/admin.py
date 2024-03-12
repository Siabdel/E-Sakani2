import os
import tempfile
from django.contrib import admin
from core import utils as sh_utils
from product import models as pro_models
from immoshop import models as sh_models
from django.conf import settings
from product.admin import ProductSpecificationInline, ProductSpecificationValueInline
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Register your models here.
class ImmoProductImageInline(admin.TabularInline):
    model = pro_models.ImmoProductImage
    # exlude = ('thumbnail_path', 'large_path',  )
    # readonly_fields = ('thumbnail_path', 'large_path',)
    max_num=1


@admin.register(pro_models.ImmoProduct)
class ImmoProductAdmin(admin.ModelAdmin):
    #inlines = [ImmoProductImageInline,]
    inlines = [ProductSpecificationValueInline, ImmoProductImageInline, ]

    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    # readonly_fields = ('thumbnail_path', 'large_path',  )
    exlude = ('thumbnail_path', 'large_path',  )
    
    def save_model__(self, request, obj, form, change):
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
                image.large_path = os.path.join("/media/images/", os.path.basename(large_path))
                image.thumbnail_path = os.path.join("/media/images/", os.path.basename(thumbnail_path))
                image.save() 

    def save_related__(self, request, form, formsets, change):
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


@admin.register(sh_models.ItemArticle)
class ItemArticleAdmin(admin.ModelAdmin):
    list_display =  [field.name for field in sh_models.ItemArticle._meta.get_fields()]
