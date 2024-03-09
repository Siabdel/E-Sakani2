from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings



class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)
class BaseProduct(models.Model):
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

    image = models.ImageField(upload_to='images/', default='images/default.png')
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    products = ProductManager()


    class Meta:
        abstract = True
        ordering = ('name', )
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name



class BaseProductImage(models.Model):
    image = models.ImageField(upload_to='upload/product_images/%Y/%m/', blank=True)
    thumbnail_path = models.CharField(_("thumbnail"), max_length=50, null=True)
    large_path     = models.CharField(_("large"), max_length=50, null=True)

    def __str__(self):
        return f"Image for {self.image.name}"

    class Meta:
        abstract = True


