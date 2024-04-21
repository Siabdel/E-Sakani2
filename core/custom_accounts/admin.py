from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from core.custom_accounts import models as acc_models

# admin.site.register(User, UserAdmin)

@admin.register(acc_models.CustomUser)
class AccountsAdmin(admin.ModelAdmin):
    list_display  = [f.name for f in acc_models.CustomUser._meta.get_fields()]
    list_display = ["username", "first_name", "last_name", "email", "is_staff", "is_superuser",  ]


@admin.register(acc_models.CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = acc_models.CustomUser
    list_display = ["first_name", "last_name", "username", "email", "country"]

    fieldsets = (
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
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


admin.site.register(acc_models.CustomUser, CustomUserAdmin) 
