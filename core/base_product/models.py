import os
from django.db import models
from django.core import checks
from django.core.cache import cache

from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth.models import User
from django.conf import settings
from django_resized import ResizedImageField
from core.utils import make_thumbnail
from polymorphic.models import PolymorphicModel, PolymorphicManager
from core import  deferred
from core.taxonomy.models import TaggedItem, MPCategory
class PolymorphicProductMetaclass(deferred.PolymorphicForeignKeyBuilder):
    @classmethod
    def perform_meta_model_check(cls, Model):
        """
        Perform some safety checks on the ProductModel being created.
        """
        if not isinstance(Model.objects, BaseProductManager):
            msg = "Class `{}.objects` must provide ModelManager inheriting from BaseProductManager"
            raise NotImplementedError(msg.format(Model.__name__))

        if not isinstance(getattr(Model, 'lookup_fields', None), (list, tuple)):
            msg = "Class `{}` must provide a tuple of `lookup_fields` so that we can easily lookup for Products"
            raise NotImplementedError(msg.format(Model.__name__))

        if not callable(getattr(Model, 'get_price', None)):
            msg = "Class `{}` must provide a method implementing `get_price(request)`"
            raise NotImplementedError(msg.format(cls.__name__))
        
class BaseProductManager(PolymorphicManager):
    def get_queryset(self):
        return super(BaseProductManager, self).get_queryset().filter(is_active=True)
class BaseProduct(PolymorphicModel,  metaclass=PolymorphicProductMetaclass):
    category = deferred.ForeignKey(MPCategory, related_name='products', null=True, blank=True, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    default_image = ResizedImageField( upload_to='upload/product_images/%Y/%m/', blank=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(_('Active'), default=True, help_text=_("Is this product publicly visible."),)
    product_code = models.CharField( _("Product code"), max_length=255, null=True, blank=True,
        help_text=_("Product code of added item."),
    )
    objects = BaseProductManager()
    #products = BaseProductManager()

    class Meta:
        abstract = True
        ordering = ('name', )
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        #index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.product.get_absolute_url()
    
    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()
    def default_image_exist(self):
        output_dir = os.path.join(settings.BASE_DIR, self.default_image.url)
        return not os.path.exists(output_dir)
    
    
    @property
    def product_model(self):
        """
        Returns the polymorphic model name of the product's class.
        """
        return self.polymorphic_ctype.model

    def get_absolute_url(self):
        """
        Hook for returning the canonical Django URL of this product.
        """
        msg = "Method get_absolute_url() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_price(self, request):
        """
        Hook for returning the current price of this product.
        The price shall be of type Money. Read the appropriate section on how to create a Money
        type for the chosen currency.
        Use the `request` object to vary the price according to the logged in user,
        its country code or the language.
        """
        msg = "Method get_price() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))
    def get_product_variant(self, **kwargs):
            """
            Hook for returning the variant of a product using parameters passed in by **kwargs.
            If the product has no variants, then return the product itself.

            :param **kwargs: A dictionary describing the product's variations.
            """
            return self

    def get_product_variants(self):
        """
        Hook for returning a queryset of variants for the given product.
        If the product has no variants, then the queryset contains just itself.
        """
        return self._meta.model.objects.filter(pk=self.pk)

    def get_availability(self, request, **kwargs):
        """
        Hook for checking the availability of a product.

        :param request:
            Optionally used to vary the availability according to the logged in user,
            its country code or language.

        :param **kwargs:
            Extra arguments passed to the underlying method. Useful for products with
            variations.

        :return: An object of type :class:`shop.models.product.Availability`.
        """
        return Availability()

    def managed_availability(self):
        """
        :return True: If this product has its quantity managed by some inventory functionality.
        """
        return False

    def is_in_cart(self, cart, watched=False, **kwargs):
        """
        Checks if the current product is already in the given cart, and if so, returns the
        corresponding cart_item.

        :param watched (bool): This is used to determine if this check shall only be performed
            for the watch-list.

        :param **kwargs: Optionally one may pass arbitrary information about the product being looked
            up. This can be used to determine if a product with variations shall be considered
            equal to the same cart item, resulting in an increase of it's quantity, or if it
            shall be considered as a separate cart item, resulting in the creation of a new item.

        :returns: The cart item (of type CartItem) containing the product considered as equal to the
            current one, or ``None`` if no product matches in the cart.
        """
        from shop.models.cart import CartItemModel
        cart_item_qs = CartItemModel.objects.filter(cart=cart, product=self)
        return cart_item_qs.first()

    def deduct_from_stock(self, quantity, **kwargs):
        """
        Hook to deduct a number of items of the current product from the stock's inventory.

        :param quantity: Number of items to deduct.

        :param **kwargs:
            Extra arguments passed to the underlying method. Useful for products with
            variations.
        """

    def get_weight(self):
        """
        Optional hook to return the product's gross weight in kg. This information is required to
        estimate the shipping costs. The merchants product model shall override this method.
        """
        return 0

    @classmethod
    def check(cls, **kwargs):
        """
        Internal method to check consistency of Product model declaration on bootstrapping
        application.
        """
        errors = super().check(**kwargs)
        try:
            cls.product_name
        except AttributeError:
            msg = "Class `{}` must provide a model field implementing `product_name`"
            errors.append(checks.Error(msg.format(cls.__name__)))
        return errors

    def update_search_index(self):
        """
        Update the Document inside the Elasticsearch index after changing relevant parts
        of the product.
        """
        documents = elasticsearch_registry.get_documents([ProductModel])
        if settings.USE_I18N:
            for language, _ in settings.LANGUAGES:
                try:
                    document = next(doc for doc in documents if doc._language == language)
                except StopIteration:
                    document = next(doc for doc in documents if doc._language is None)
                document().update(self)
        else:
            document = next(doc for doc in documents)
            document().update(self)



class BaseImage(PolymorphicModel):
    title = models.CharField(_('Titre'), max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=255, db_index=True, null=True, blank=True)
    image = models.ImageField(upload_to='upload/product_images/%Y/%m/', blank=True)
    thumbnail_path = models.CharField(_("thumbnail"), max_length=50, null=True)
    large_path     = models.CharField(_("large"), max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def save__(self, *args, **kwargs):
        #raise Exception(f"args {args} kwargs = {kwargs}")
        img_100 = make_thumbnail(self.image, size=(100, 100))
        img_800 = make_thumbnail(self.image, size=(800, 600))
        
        output_dir = os.path.join(settings.MEDIA_ROOT, "images")
         # Enregistre les images traitées
        base_name = os.path.basename(img_100.name)
        self.thumbnail = os.path.join(output_dir, f"thumb_100x100_{base_name}")
        #
        base_name = os.path.basename(img_100.name)
        self.large_path = os.path.join(output_dir, f"large_800x600_{base_name}")
        #raise Exception(f"image attribues = {img_100.name}")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Image for {self.image.name}"

    class Meta:
        abstract = True
        
    def product_type(self):
        """
        Returns the polymorphic type of the product.
        """
        return force_str(self.polymorphic_ctype)
    product_type.short_description = _("Product type")

    @property
    def product_model(self):
        """
        Returns the polymorphic model name of the product's class.
        """
        return self.polymorphic_ctype.model

    def get_absolute_url(self):
        """
        Hook for returning the canonical Django URL of this product.
        """
        msg = "Method get_absolute_url() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def get_price(self, request):
        """
        Hook for returning the current price of this product.
        The price shall be of type Money. Read the appropriate section on how to create a Money
        type for the chosen currency.
        Use the `request` object to vary the price according to the logged in user,
        its country code or the language.
        """
        msg = "Method get_price() must be implemented by subclass: `{}`"
        raise NotImplementedError(msg.format(self.__class__.__name__))


class BaseProject(PolymorphicModel):
    """
    Base Project model
    """
    title   = models.CharField(max_length=100, verbose_name=_('title'))
    slug    = models.SlugField(max_length=150, unique=True ,db_index=True)
    description = models.TextField(null=True, blank=True, verbose_name=_('description'))
    author      = models.ForeignKey('auth.User', related_name='created_projects', null=True, blank=True, verbose_name=_('created by'), on_delete=models.SET_NULL)
    manager     = models.ForeignKey('auth.User', related_name='managed_projects', null=True, blank=True, verbose_name=_('project manager'), on_delete=models.SET_NULL)
    status      = models.CharField(_('status'), choices= settings.PROJECT_STATUS_CHOICES, default= settings.PROJECT_DEFAULT_STATUS, max_length=10 )
    visibilite  = models.CharField(max_length=100, choices=settings.VISIBILITE_CHOICES, default=settings.VISIBILITE_DEFAULT, verbose_name=_('visiblite'))
    created     = models.DateTimeField(auto_now_add=True, verbose_name=_('created on'))
    due_date    = models.DateTimeField(verbose_name=_("date d\'echeance"))
    closed      = models.DateTimeField(null=True, blank=True, verbose_name=_('closed on'))
    start_date  = models.DateTimeField(verbose_name=_('date debut'),  ) # timezone.now()
    end_date    = models.DateTimeField(verbose_name=_('date fin'), null=True, blank=True)
    comment     = models.TextField(null=True, blank=True)
    default_image = ResizedImageField( upload_to='upload/product_images/%Y/%m/', blank=True)

    class Meta:
        abstract = True
        ordering = ['slug']
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return "%s" % self.title

    def save(self):
        if self.status in settings.PROJECT_CLOSE_STATUSES :
            if self.closed is None:
                self.closed = timezone.now()
            self.closed = None

        # super save
        super(BaseProject, self).save()

    @property
    def closed(self):
        if self.end_date :
            return True
        
    def working_hours(self):
        count = 0
        for ticket in self.tickets.all():
            count += ticket.working_hours()
        return count
    
       #@models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {"pk": self.pk})

    #@models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {"pk": self.pk})

    #@models.permalink
    def get_edit_url(self):
        return ('project_edit', (), {"pk": self.pk})

    #@models.permalink
    def get_delete_url(self):
        return ('project_delete', (), {"pk": self.pk})

    def add_tags(self, tag_label):
        """
        b = Bookmark(url='https://www.djangoproject.com/')
        >>> b.save()
        >>> t1 = TaggedItem(content_object=b, tag='django')
        >>> t1.save()
        # les tags de object Bookmark
        tags = GenericRelation(TaggedItem, related_query_name='bookmark')
        # types de recherches manuellement :
        >>> bookmarks = Bookmark.objects.filter(url__contains='django')
        >>> bookmark_type = ContentType.objects.get_for_model(Bookmark)
        >>> TaggedItem.objects.filter(content_type__pk=bookmark_type.id, object_id__in=bookmarks)
        """
        t1 = TaggedItem(content_object=self, object_id=self.pk, tag=tag_label)
        t1.save()

    def get_tag_project(self):
        return TaggedItem.objects.filter(content_type__pk=self.id)

   
    # les tags de object Bookmark
    def get_all_tags_project(self):
        return ContentType.objects.get_for_model(Project)

    # add  partenaire du project
    def add_partenaire_client(self, partenaire_id, partenaire_name, partenaire_type='C'):
        """
        pp1 = models.Project.objects.get(pk=25)
        cli1 = of_models.DjangoClient.objects.get(codeclie=222)
        cli2 = of_models.DjangoClient.objects.get(codeclie=223)
        t1 = models.Partenaire(content_object=pp1, tiers=cli1.codeclie)
        t2 = models.Partenaire(content_object=pp1, tiers=cli2.codeclie)
        t1.save() ; t2.save()
        models.Partenaire.objects.filter(content_type=pp1)
        """

        t1 = Partenaire(content_object=self,
                        tiers_id=partenaire_id,
                        tiers_name=partenaire_name,
                        tiers_type=partenaire_type)
        t1.save()

    # get partenaire du project
    def get_partenaires_project(self):
        return Partenaire.objects.filter(object_id=self.pk)
            ## Upload files

    # add document du project
    def add_document(self, document):
        """
        """
        doc= GDocument(content_object=self, document = document)
        doc.save()

    # get pieces jointes au project
    def get_documents_project(self):
        return self.documents.all()
    # get pieces jointes au project
 
