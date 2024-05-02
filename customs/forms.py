from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm 
from customs.models import Custom 
from django import forms

#
User = get_user_model()

class AccountUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', )

class CustomCreatForm(forms.ModelForm):

    class Meta:
        model = Custom
        fields = ('email', 'first_name', 'last_name', 'company',
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

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Custom
        fields = ('email', 'first_name', 'last_name', 'company',
                  'address1', 'address2', 'country', 'phone_number',  )