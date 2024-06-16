# models.py
from typing import Any, MutableMapping
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
# from ofschedule.models import DjangoMachine
from config import settings
from core.base_product import models as base_models
from core.shop import models as sh_models
from core.product import models as pro_models
from project import models as proj_models

class CarProduct(pro_models.Product):
    project = models.ForeignKey(proj_models.Project, on_delete=models.CASCADE)
 
class ImmoProduct(pro_models.Product):
    project = models.ForeignKey(proj_models.Project, on_delete=models.CASCADE)
    

    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(pro_models.ProductImage):
    pass
    
class ImmoProductSpecificationValue(pro_models.ProductSpecificationValue):
    """ The product specification value table hold each of the 
    product individal specification or bespoke features.
    """
    pass