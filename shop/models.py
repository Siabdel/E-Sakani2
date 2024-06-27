# models.py
from typing import Any, MutableMapping
from django.db import models
from django.core import checks
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from polymorphic.models import PolymorphicModel, PolymorphicManager
from django.contrib.auth.models import User
# from ofschedule.models import DjangoMachine
from django.conf import settings
from core.base_shop import models as bshop_models
from core import deferred
from collections import OrderedDict
from product import models as pro_models
from core import  deferred

# -----------------------------------------
# -- Item CART (Panier d'articles en base) 
# -----------------------------------------
from polymorphic.models import PolymorphicModel, PolymorphicManager
class ShopCartManager(PolymorphicManager):
    def get_or_create_cart(self, user, titre="Cart1 test"):
        try:
            # Récupérer le panier existant de l'utilisateur s'il en a un
            cart = self.get(created_by=user, statut='ACT')
        except Exception as err :
            # Créer un nouveau panier pour l'utilisateur s'il n'en a pas
            cart = self.create(created_by=user, statut='ACT')
        # save
        cart.save()
        return cart
class ShopCart(bshop_models.BaseCart): 
    class StatusChoice(models.TextChoices):
        ACTIVE = 'ACT', _('Encours')
        CLOS = 'CLO', _('cloturé'), 
    titre       = models.CharField(max_length=50, blank=True, null=True)
    statut      = models.CharField(max_length=10, choices=StatusChoice.choices, default=StatusChoice.ACTIVE) # 1- encours 2- Cloturee
    created_at     = models.DateTimeField(auto_now_add=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))
    comment     = models.TextField(null=True, blank=True, )
    objects = ShopCartManager()

    class Meta:
        verbose_name = _('ShopCart')
        verbose_name_plural = _('ShopCart')
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        self.titre  = self.titre if self.titre  else f"Panier : {self.pk}" 
        super(ShopCart, self).save(*args, **kwargs) 
    
    def sum_items(self):
        total_quantity = sum(item.quantity for item in self.item_articles.all())
        return total_quantity
 
    def __str__(self):
        self.titre  = self.titre if self.titre  else f"Panier : {self.id}" 
        return f"{self.titre} - {self.statut} - {self.created_at}"
class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'post' in kwargs:
            kwargs['content_type'] = ContentType.objects.get_for_model(type(kwargs['product']))
            kwargs['object_id'] = kwargs['product'].pk
            del(kwargs['product'])
        return super(ItemManager, self).get(*args, **kwargs)
    
    def get_or_create_item(self, *args, **kwargs): 
        created = False
        try :
            #return super(ItemManager, self).get(*args, **kwargs)
            return ItemArticle.get_product() , created
        except Exception as err :
            return ItemArticle.objects.get_or_create(*args, **kwargs) 

class ItemArticle(bshop_models.BaseCartItem):  
    quantity = models.IntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                     verbose_name=_('unit price'))  