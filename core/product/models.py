from datetime import datetime
from core import deferred
from django.utils import timezone
from django.db import models
from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from polymorphic.models import PolymorphicModel, PolymorphicManager
from django.contrib.auth.models import User
from django.conf import settings
from core.taxonomy import models as tax_models
from core.base_product import models as base_models
from core.taxonomy import models as core_models
from core.profile.models import UProfile
from core.profile.models import Societe
from core.taxonomy.models import TaggedItem, MPCategory

# Create your Product.
class Product(base_models.BaseProduct):
    """_summary_
    """
    product_name = models.CharField(max_length=100, null=True, blank=True)
    lookup_fields = ('id', 'slug')  # Ajout de lookup_fields
    ## project = models.ForeignKey(proj_models.Project, on_delete=models.CASCADE)

    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("shop:product_car_detail", args=[str(self.id)])



    def product_type(self):
        return "product"
    class Meta :
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        

class ProductType(models.Model):
    name = models.CharField(_('Name'), max_length=150, db_index=True)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name
        
        
class ProductSpecification(models.Model):
    product_type = models.ForeignKey(ProductType, verbose_name=_("Specification"), 
                                     on_delete=models.RESTRICT)
    name = models.CharField(_('Name'), max_length=150, db_index=True)

    def __str__(self):
        return self.name
    
class ProductSpecificationValue(PolymorphicModel):
    """ The product specification value table hold each of the 
    product individal specification or bespoke features.
    """
    product = models.ForeignKey(Product, verbose_name=_(""), on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value   = models.CharField(_("Value"), max_length=255)
    

class ProductImage(base_models.BaseImage):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
