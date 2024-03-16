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

class ImmoProduct(base_models.BaseProduct):
    product_type = models.ForeignKey(pro_models.ProductType, verbose_name=_(""), on_delete=models.CASCADE)
    category = models.ForeignKey(pro_models.MPCategory, null=True, blank=True, 
                                 related_name='immo_products', on_delete=models.CASCADE)
    
    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(base_models.BaseProductImage):
    cart = models.ForeignKey(sh_models.ShopCart, related_name='items', on_delete=models.CASCADE )
    # product as generic relation
    content_object = GenericForeignKey('content_type', 'object_id')
    # My Manager 