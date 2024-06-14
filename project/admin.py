from django.utils import timezone
import tempfile
from core import utils as sh_utils
from django.conf import settings
from django.contrib.auth.models import User
from core.base_product import models as base_models
from django.contrib import admin
from  mptt.admin  import MPTTModelAdmin
# Register your models here.
from project import models as proj_models 
from immoshop import models as immo_models 
from immoshop.admin import BaseArticleAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline



# Register your models here.
##
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldWidget


class CityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }


class ProductInline(admin.TabularInline):
    model = immo_models.ImmoProduct
    fields = ('name', 'slug', 'price','stock',)
    extra = 1

class ProjectImagesInline(admin.TabularInline):
    model = proj_models.ProjectImage
    readonly_fields = ('thumbnail_path', 'large_path',)
    fields = ('title', 'image',  )
    extra = 0

@admin.register(proj_models.Project)
class ProjectAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    #base_model = base_models.BaseProject
    inlines = [ProjectImagesInline, ProductInline, ]
    # list_display =  [field.name for field in proj_models.Project._meta.get_fields()]
    list_display =  ['title', 'slug', 'manager', 'start_date', 'visibilite', 'closed',  ]
    #exclude = ["author", "manager", ]
    prepopulated_fields = {'slug': ('title',), }

    fieldsets = (
        (
            "Required Information", {
                # Section Description
                "description" : "Enter the Project information",
                # Group Make and Model
                "fields" : (( 'societe', 'category',),
                            ('title', 'slug', 'description', ),
                            ),
            }, 
        ),
        
        (
            "Required Information 2", {
                "fields" : (
                    ('manager', 'status', 'visibilite'),
                    ('due_date', 'start_date', 'end_date'),
                ),
            },
        ),
        (
            "Information supplementaire comment", {
                "classes": ("collapse",),
                "fields" : (
                    'default_image',
                    'lon',
                    'lat',
                    'comment', 
                ),
            },
        ),
    )
    
    def get_changeform_initial_data(self, request):
        return {
            'author': 1, 
            'manager': 1, 
            'start_date': timezone.now(),
            'societe' : 1,
            }


   
admin.register(CityAdmin)