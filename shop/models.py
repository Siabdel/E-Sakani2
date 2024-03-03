from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
# from ofschedule.models import DjangoMachine
from django.conf import settings

# -----------------------------------------
# -- Item CART (Panier d'articles en base) 
# -----------------------------------------
class ShopCart(models.Model):
    class StatusChoice(models.TextChoices):
        ACTIVE = 'ACT', _('Encours')
        CLOS = 'CLO', _('cloturé'), 
    titre       = models.CharField(max_length=50, blank=True, null=True)
    statut      = models.CharField(max_length=10, choices=StatusChoice.choices, default=StatusChoice.ACTIVE) # 1- encours 2- Cloturee
    created_at     = models.DateTimeField(auto_now_add=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))
    comment     = models.TextField(null=True, blank=True, )

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('cartsOf')
        ordering = ('-created_at',)

    def __str__(self):
        return "{}".format(self.titre)
class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'post' in kwargs:
            kwargs['content_type'] = ContentType.objects.get_for_model(type(kwargs['product']))
            kwargs['object_id'] = kwargs['product'].pk
            del(kwargs['product'])
        return super(ItemManager, self).get(*args, **kwargs)

class ItemRaw(models.Model):
    raw_message = models.JSONField()

class ItemArticle(models.Model):    
    cart = models.ForeignKey(ShopCart, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, 
                                     verbose_name=_('unit price'))
     # product as generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField() 
    content_object = GenericForeignKey('content_type', 'object_id')
    # quand
    created_at  = models.DateTimeField(auto_now_add=True)
    # My Manager 
    objects = ItemManager()
    class Meta:
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
        return "product : {}".format(self.product.titre)