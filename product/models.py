from django.db import models
from django.urls import reverse, resolve
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings
from core.taxonomy import models as tax_models
from core.base_product import models as base_models
from core.taxonomy import models as core_models

from mptt.models import MPTTModel, TreeForeignKey

class MPCategory(MPTTModel):
    """ Category table implement MPTT"""
    name = models.CharField(_('Category Name'), help_text=_('Requird and uniq'), 
                              max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True ,db_index=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class MPTTModel:
        ordering = ('name', )
        ordering_insertion_by = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('immoshop:product_list_by_category', args=[self.slug])
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
    
class ProductSpecificationValue(models.Model):
    """ The product specification value table hold each of the 
    product individal specification or bespoke features.
    """
    product = models.ForeignKey("ImmoProduct", verbose_name=_(""), on_delete=models.CASCADE)
    specification = models.ForeignKey(ProductSpecification, on_delete=models.RESTRICT)
    value   = models.CharField(_("Value"), max_length=255)
    
# Create your Product.
class Product(base_models.BaseProduct):
    category = models.ForeignKey(MPCategory, related_name='products', 
                                 null=True, blank=True,
                                 on_delete=models.CASCADE)

class ProductImage(base_models.BaseProductImage):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    

class ImmoProduct(base_models.BaseProduct):
    product_type = models.ForeignKey(ProductType, verbose_name=_(""), on_delete=models.CASCADE)
    category = models.ForeignKey(MPCategory, null=True, blank=True, 
                                 related_name='immo_products', on_delete=models.CASCADE)
    
    
    def get_images(self):
        return self.images.all()

    def get_absolute_url(self):
        return reverse("immoshop:product_immo_detail", args=[str(self.id)])

class ImmoProductImage(base_models.BaseProductImage):
    product = models.ForeignKey(ImmoProduct, related_name="images", on_delete=models.CASCADE)