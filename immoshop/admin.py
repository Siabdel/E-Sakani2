import os
import tempfile
from django.contrib import admin
from product import models as pro_models
from shop import models as sh_models
from shop import utils as sh_utils
from immoshop import models as msh_models
from django.conf import settings


# Register your models here.
# 
class ImmoProductImageInline(admin.TabularInline):
    model = msh_models.ImmoProductImage
    exlude = ('thumbnail_path', 'large_path',  )
    readonly_fields = ('thumbnail_path', 'large_path',)


## @admin.register(msh_models.ImmoProduct)
class ImmoProductAdmin(admin.ModelAdmin):
    inlines = [ImmoProductImageInline]

    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    # readonly_fields = ('thumbnail_path', 'large_path',  )
    exlude = ('thumbnail_path', 'large_path',  )
    
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
                image.large_path = os.path.join("/media/images/", os.path.basename(large_path))
                image.thumbnail_path = os.path.join("/media/images/", os.path.basename(thumbnail_path))
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



admin.site.register(msh_models.ImmoProduct, ImmoProductAdmin)
