# models.py
from typing import Any, MutableMapping
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
# from ofschedule.models import DjangoMachine
from django.conf import settings
from core.base_product import models as base_models
from core.shop import models as sh_models
from core.product import models as pro_models
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter


class ImmoProduct(pro_models.Product):
    
    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(pro_models.ProductImage):
    pass
    
class ImmoProductSpecificationValue(models.Model):
    """ The product specification value table hold each of the 
    product individal specification or bespoke features.
    """
    product = models.ForeignKey(ImmoProduct, verbose_name=_(""), on_delete=models.CASCADE)
    specification = models.ForeignKey(pro_models.ProductSpecification, on_delete=models.RESTRICT)
    value   = models.CharField(_("Value"), max_length=255)
    