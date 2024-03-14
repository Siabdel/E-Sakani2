import os
import tempfile
from django.contrib import admin
from product import models as pro_models
from shop import models as sh_models
from core import utils as sh_utils
from django.conf import settings

@admin.register(pro_models.Category )
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = pro_models.ProductImage
    exlude = ('thumbnail_path', 'large_path',  )
    readonly_fields = ('thumbnail_path', 'large_path',  )


@admin.register(pro_models.Product )
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('title',)}
    exlude = ('thumbnail_path', 'large_path', 'title', 'slug', )
    
    def save_formset__(self, request, form, formset, change):
        """ Cette méthode est appelée lors de l'enregistrement des 
        objets dans les formsets associés à votre modèle. 
        Elle vous permet de contrôler le comportement lors de l'enregistrement 
        de ces objets.
        """
        super().save_formset(request, form, formset, change)
        output_dir = os.path.join(settings.MEDIA_ROOT, "images")
        # Process newly uploaded images

        #raise Exception("thumbnail retour {} ".format( request.FILES))
        for uploaded_image in request.FILES.getlist('images-0-image'):
            # processus de resize images
            # Enregistrer l'image téléchargée sur le disque temporaire
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in uploaded_image.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
            
            # Créer une nouvelle instance de ProductImage pour chaque fichier téléchargé
            new_image = pro_models.ProductImage(product=obj, image=uploaded_image)
        
            thumbnail_path, large_path = sh_utils.process_resize_image(new_image, output_dir)
            uploaded_image.large_path = os.path.join("/media/images/", os.path.basename(large_path))
            uploaded_image.thumbnail_path = os.path.join("/media/images/", os.path.basename(thumbnail_path))
            # Enregistrer le ProductImage
            #uploaded_image.save()
        
        return formset.save()            
            
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

@admin.register(pro_models.ProductImage )
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'thumbnail_path', 'large_path' ]
