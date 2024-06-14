import os
from django.db import models
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


class ProductManager(PolymorphicManager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)
class BaseProduct(PolymorphicModel):
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
    product_code = models.BigIntegerField(_("Product Code"), null=True, blank=True)
    objects = ProductManager()
    products = ProductManager()

    class Meta:
        abstract = True
        ordering = ('name', )
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
        #output_dir = os.path.join("/home/django/Depots/www/Back-end/Django/envEsakani/E-sakani/", self.default_image.url)
        #raise Exception(output_dir)
        # /media/upload/product_images/2024/03/logo-appartement_I3pvvys.jpg
        return not os.path.exists(output_dir)

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

 
class BaseItemArticle(models.Model):    
    quantity = models.IntegerField(verbose_name=_('quantity'),  default=1)

    unit_price = models.DecimalField(max_digits=10, 
                                     decimal_places=2, 
                                     verbose_name=_('unit price'))
     # product as generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField() 
    # quand
    created_at  = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
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
        return "product : {}".format(self.product)
    

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
 
