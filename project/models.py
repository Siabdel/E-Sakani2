from datetime import datetime
from django.utils import timezone
from django.db import models
from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from core.taxonomy import models as tax_models
from core.base_product import models as base_models
from core.taxonomy import models as core_models
from polymorphic.models import PolymorphicModel, PolymorphicManager
from mptt.models import MPTTModel, TreeForeignKey
from core.profile.models import UProfile
from core.profile.models import Societe
from core.taxonomy.models import TaggedItem, MPCategory
# from mapwidgets.widgets import GooglePointField
##from django.contrib.gis.db import models as gmodels
from core import deferred

# Create your models here.
class Partenaire(models.Model):
    tiers_id    = models.CharField(max_length=3)
    tiers_name  = models.CharField(max_length=100)
    tiers_type  = models.CharField(max_length=1, choices=(('C', 'Client'), ('F', 'Fornisseur')), default='F')
    created     = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # Listed below are the mandatory fields for a generic relation
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    content_object  = GenericForeignKey('content_type', 'object_id')


    def __str__(self):
        return "tiers=%s id=%s" % (self.tiers_type , self.tiers_id)

class Project(base_models.BaseProject):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE)
    category = models.ForeignKey(MPCategory, related_name='projetcs', null=True, blank=True, on_delete=models.CASCADE)
    partenaire  = GenericRelation(Partenaire, null=True, blank=True) # clients ou fournisseurs
    documents   = GenericRelation('taxonomy.GDocument',  null=True, blank=True) #  les documents rattachées
    lon = models.FloatField(null=True, blank=True) # longitude
    lat = models.FloatField(null=True, blank=True) # latitude
    #location = gmodels.PointField(null=True, blank=True)


class ProjectImage(base_models.BaseImage) :
    project = models.ForeignKey(Project, related_name='images', null=True, blank=True, on_delete=models.CASCADE)