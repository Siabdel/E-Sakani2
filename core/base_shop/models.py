
from collections import OrderedDict
from django.core import checks
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel, PolymorphicManager
from core import deferred
from core.models.customer import CustomerModel
from core.base_product import models as bpro_models


class CartManager(PolymorphicManager):
    """
    The Model Manager for any Cart inheriting from BaseCart.
    """
    def get_from_request(self, request):
        """
        Return the cart for current customer.
        """
        if request.customer.is_visitor:
            raise self.model.DoesNotExist("Cart for visiting customer does not exist.")
        if not hasattr(request, '_cached_cart') or request._cached_cart.customer.user_id != request.customer.user_id:
            request._cached_cart, created = self.get_or_create(customer=request.customer)
        return request._cached_cart

    def get_or_create_from_request(self, request):
        has_cached_cart = hasattr(request, '_cached_cart')
        if request.customer.is_visitor:
            request.customer = CustomerModel.objects.get_or_create_from_request(request)
            has_cached_cart = False
        if not has_cached_cart or request._cached_cart.customer.user_id != request.customer.user_id:
            request._cached_cart, created = self.get_or_create(customer=request.customer)
        return request._cached_cart

class BaseCart(PolymorphicModel):

    """
    The fundamental part of a shopping cart.
    """
    customer = deferred.OneToOneField( 'BaseCustomer', on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_("Customer"),
    )

    created_at = models.DateTimeField( _("Created at"), auto_now_add=True,)

    updated_at = models.DateTimeField( _("Updated at"), auto_now=True,)

    extra = models.JSONField(verbose_name=_("Arbitrary information for this cart"), null=True)

    # our CartManager determines the cart object from the request.
    objects = CartManager()

    class Meta:
        abstract = True
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.extra_rows = OrderedDict()
        self._cached_cart_items = None
        self._dirty = True
    

class CartItemManager(PolymorphicManager):
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


class BaseCartItem(PolymorphicModel):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased
    """
    cart = deferred.ForeignKey(BaseCart, on_delete=models.CASCADE, related_name='item_articles',)
    product = deferred.ForeignKey( bpro_models.BaseProduct, on_delete=models.CASCADE,)

    updated_at = models.DateTimeField( _("Updated at"), auto_now=True,)

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
        

