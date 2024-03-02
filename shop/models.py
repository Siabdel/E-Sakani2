from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True ,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
    
    def get_images(self):
        return self.images.all()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='upload/product_images/%Y/%m/', blank=True)
    thumbnail_path = models.CharField(_("thumbnail"), max_length=50, null=True)
    large_path     = models.CharField(_("large"), max_length=50, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"


#----------------------
#- Product Attribus 

class ProductItem(models.Model):
    """
    Déclinaison de produit déterminée par des attributs comme la couleur, etc.
    """

    class Meta:
        verbose_name = "Déclinaison Produit"

    product     = models.ForeignKey('Product', on_delete=models.CASCADE)
    code        = models.CharField(max_length=10, null=True, blank=True, unique=True)
    code_ean13  = models.CharField(max_length=13)
    attributes  = models.ManyToManyField("ProductAttributeValue", related_name="product_item", null=True, blank=True)

    def __str__(self):
        return u"{0} [{1}]".format(self.product.name, self.code)

class ProductAttribute(models.Model):
    """
    Attributs produit
    """
    class Meta:
        verbose_name = "Attribut"

    name =  models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ProductAttributeValue(models.Model):
    """
    Valeurs des attributs
    """
    class Meta:
        verbose_name = "Valeur attribut"
        ordering = ['position']

    value              = models.CharField(max_length=100)
    product_attribute  = models.ForeignKey('ProductAttribute', verbose_name="Unité", on_delete=models.CASCADE)
    position           = models.PositiveSmallIntegerField("Position", null=True, blank=True)

    def __str__(self):
        return u"{0} [{1}]".format(self.value, self.product_attribute)