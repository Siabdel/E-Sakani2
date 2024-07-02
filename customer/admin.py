from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomCreatForm
from customer import models as acc_models

# admin.site.register(User, UserAdmin)

# Register your models here.
@admin.register(acc_models.Customer)
class AccountsAdmin(admin.ModelAdmin):
    list_display  = [f.name for f in acc_models.Customer._meta.get_fields()]
    list_display =  ('email', 'first_name', 'last_name', 'company',
                  'address1', 'address2', 'country', 'phone_number',  )
    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                )
            },
        ),
        (
            "Company Info",
            {
                "classes": ("collapse",),
                "fields": (
                    "company",
                    "company_logo",
                    "address1",
                    "address2",
                    "country",
                ),
            },
        ),
    )

class CustomUserAdmin(UserAdmin):
    add_form = CustomCreatForm
    form = CustomUserChangeForm
    model = acc_models.Customer
    list_display = ["first_name", "last_name", "email", "country", ]

    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "phone_number",
                )
            },
        ),
        (
            "Company Info",
            {
                "classes": ("collapse",),
                "fields": (
                    "company",
                    "company_logo",
                    "address1",
                    "address2",
                    "country",
                ),
            },
        ),
        (
            "Permissions",
            {
                "classes": ("collapse",),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )


## admin.site.register(Customer, CustomUserAdmin) 