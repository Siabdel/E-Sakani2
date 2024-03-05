from django.db import models
from product import models as pro_models
from shop import models as sh_models
from django.urls import reverse, resolve
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.
class ImmoProduct(pro_models.BaseProduct):
    category = models.ForeignKey(pro_models.Category, null=True, blank=True, 
                                 related_name='immo_products', on_delete=models.CASCADE)
    

    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(pro_models.BaseProductImage):
    product = models.ForeignKey(ImmoProduct, related_name="images", on_delete=models.CASCADE)