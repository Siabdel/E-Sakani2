import os
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings
from django_resized import ResizedImageField
from core.utils import make_thumbnail
from polymorphic.models import PolymorphicModel, PolymorphicManager


class ProductManager(PolymorphicManager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)
class BaseProduct(PolymorphicModel):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    default_image = ResizedImageField( upload_to='upload/product_images/%Y/%m/', blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    product_code = models.BigIntegerField(_("Product Code"), null=True, blank=True)
    objects = ProductManager()
    products = ProductManager()

    class Meta:
        abstract = True
        ordering = ('name', )
        #index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.product.get_absolute_url()
    
    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()
    def default_image_exist(self):
        output_dir = os.path.join(settings.BASE_DIR, self.default_image.url)
        #output_dir = os.path.join("/home/django/Depots/www/Back-end/Django/envEsakani/E-sakani/", self.default_image.url)
        #raise Exception(output_dir)
        # /media/upload/product_images/2024/03/logo-appartement_I3pvvys.jpg
        return not os.path.exists(output_dir)

class BaseProductImage(models.Model):
    title = models.CharField(_('Titre'), max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=255, db_index=True, null=True, blank=True)
    image = models.ImageField(upload_to='upload/product_images/%Y/%m/', blank=True)
    thumbnail_path = models.CharField(_("thumbnail"), max_length=50, null=True)
    large_path     = models.CharField(_("large"), max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def save__(self, *args, **kwargs):
        #raise Exception(f"args {args} kwargs = {kwargs}")
        img_100 = make_thumbnail(self.image, size=(100, 100))
        img_800 = make_thumbnail(self.image, size=(800, 600))
        
        output_dir = os.path.join(settings.MEDIA_ROOT, "images")
         # Enregistre les images traitées
        base_name = os.path.basename(img_100.name)
        self.thumbnail = os.path.join(output_dir, f"thumb_100x100_{base_name}")
        #
        base_name = os.path.basename(img_100.name)
        self.large_path = os.path.join(output_dir, f"large_800x600_{base_name}")
        #raise Exception(f"image attribues = {img_100.name}")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Image for {self.image.name}"

    class Meta:
        abstract = True


class BaseItemArticle(models.Model):    
    quantity = models.IntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, 
                                     verbose_name=_('unit price'))
     # product as generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField() 
    # quand
    created_at  = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        verbose_name = _('ItemArticle')
        verbose_name_plural = _('ItemArticles')
        ordering = ('-created_at',)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

    # product
    def get_product(self):
        return self.content_type.get_object_for_this_type(pk=self.object_id)
    
    def set_product(self, product):
        self.content_type = ContentType.objects.get_for_model(type(product))
        self.object_id = product.pk
    
    product = property(get_product, set_product) 

    def __str__(self):
        return "product : {}".format(self.product)
    
