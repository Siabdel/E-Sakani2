from django.db import models
from django.urls import reverse, resolve
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings
from core.taxonomy import models as tax_models
from core.base_product import models as bpro_models
from core.taxonomy import models as core_models

# Create your models here.
class Product(bpro_models.BaseProduct):
    category = models.ForeignKey(core_models.Category, related_name='products', 
                                 null=True, blank=True,
                                 on_delete=models.CASCADE)

class ProductImage(bpro_models.BaseProductImage):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    

class ImmoProduct(bpro_models.BaseProduct):
    category = models.ForeignKey(core_models.Category, null=True, blank=True, 
                                 related_name='immo_products', on_delete=models.CASCADE)
    
    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(bpro_models.BaseProductImage):
    product = models.ForeignKey(ImmoProduct, related_name="images", on_delete=models.CASCADE)