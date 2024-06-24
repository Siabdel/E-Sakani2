# models.py
from typing import Any, MutableMapping
from django.db import models
from django.core import checks
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
# from ofschedule.models import DjangoMachine
from django.conf import settings
from core.base_shop import models as bshop_models
from core import deferred
from collections import OrderedDict
from core.base_product import models as base_models

# -----------------------------------------
# -- Item CART (Panier d'articles en base) 
# -----------------------------------------
class ShopCartManager(models.Manager):
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


class CartItemManager(models.Manager):
    """
    Customized model manager for our CartItem model.
    """

    def get_or_create(self, **kwargs):
        """
        Create a unique cart item. If the same product exists already in the given cart,
        increase its quantity, if the product in the cart seems to be the same.
        """
        cart = kwargs.pop('cart')
        product = kwargs.pop('product')
        quantity = int(kwargs.pop('quantity', 1))

        # add a new item to the cart, or reuse an existing one, increasing the quantity
        watched = not quantity
        cart_item = product.is_in_cart(cart, watched=watched, **kwargs)
        if cart_item:
            if not watched:
                cart_item.quantity += quantity
            created = False
        else:
            cart_item = self.model(cart=cart, product=product, quantity=quantity, **kwargs)
            created = True

        cart_item.save()
        return cart_item, created

    def filter_cart_items(self, cart, request):
        """
        Use this method to fetch items for shopping from the cart. It rearranges the result set
        according to the defined modifiers.
        """
        cart_items = self.filter(cart=cart, quantity__gt=0).order_by('updated_at')
        for modifier in cart_modifiers_pool.get_all_modifiers():
            cart_items = modifier.arrange_cart_items(cart_items, request)
        return cart_items

    def filter_watch_items(self, cart, request):
        """
        Use this method to fetch items from the watch list. It rearranges the result set
        according to the defined modifiers.
        """
        watch_items = self.filter(cart=cart, quantity=0)
        for modifier in cart_modifiers_pool.get_all_modifiers():
            watch_items = modifier.arrange_watch_items(watch_items, request)
        return watch_items


class BaseCartItem(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased
    """
    cart = deferred.ForeignKey(
        bshop_models.BaseCart,
        on_delete=models.CASCADE,
        related_name='item_articles',
    )

    product = deferred.ForeignKey(
        base_models.BaseProduct,
        on_delete=models.CASCADE,
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Product code of added item."),
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

    extra = models.JSONField(verbose_name=_("Arbitrary information for this cart item"),
                             null=True, blank=True)

    objects = CartItemManager()

    class Meta:
        abstract = True
        verbose_name = _("Cart item")
        verbose_name_plural = _("Cart items")

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        allowed_types = ['IntegerField', 'SmallIntegerField', 'PositiveIntegerField',
                         'PositiveSmallIntegerField', 'DecimalField', 'FloatField']
        for field in cls._meta.fields:
            if field.attname == 'quantity':
                if field.get_internal_type() not in allowed_types:
                    msg = "Class `{}.quantity` must be of one of the types: {}."
                    errors.append(checks.Error(msg.format(cls.__name__, allowed_types)))
                break
        else:
            msg = "Class `{}` must implement a field named `quantity`."
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors

    def __init__(self, *args, **kwargs):
        # reduce the given fields to what the model actually can consume
        
        all_field_names = [field.name for field in self._meta.get_fields(include_parents=True)]
        model_kwargs = {k: v for k, v in kwargs.items() if k in all_field_names}
        super().__init__(*args, **model_kwargs)
        self.extra_rows = OrderedDict()
        self._dirty = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.cart.save(update_fields=['updated_at'])
        self._dirty = True

    def update(self, request):
        """
        Loop over all registered cart modifier, change the price per cart item and optionally add
        some extra rows.
        """
        if not self._dirty:
            return
        self.refresh_from_db()
        self.extra_rows = OrderedDict()  # reset the dictionary
        for modifier in cart_modifiers_pool.get_all_modifiers():
            modifier.process_cart_item(self, request)
        self._dirty = False
        

CartItemModel = deferred.MaterializedModel(BaseCartItem)

class ItemArticle(BaseCartItem):  
    quantity = models.IntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                     verbose_name=_('unit price'))  