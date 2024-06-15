
from collections import OrderedDict
from django.core import checks
from django.db import models
from django.utils.translation import gettext_lazy as _
from core import deferred
from core.models.customer import CustomerModel


class CartManager(models.Manager):
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

class BaseCart(models.Model, metaclass=deferred.ForeignKeyBuilder):
    """
    The fundamental part of a shopping cart.
    """
    customer = deferred.OneToOneField(
        'BaseCustomer',
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_("Customer"),
    )

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True,
    )

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