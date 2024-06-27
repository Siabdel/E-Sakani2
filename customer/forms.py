from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm 
from customer.models import Customer 
from django import forms

#
User = get_user_model()

class AccountUserCreationForm(UserCreationForm):
       
    class Meta:
        model = get_user_model()
        fields = ('email',  )

class CustomCreatForm(forms.ModelForm):

    class Meta:
        model = Customer
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
        model = Customer
        fields = ('email', 'first_name', 'last_name', 'company',
                  'address1', 'address2', 'country', 'phone_number',  )
            


class CustomerForm(forms.ModelForm):
    
    fieldsets = [
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
                ]
    class Meta:
        model = Customer
        fields = "__all__" 

CustomFormSet = forms.inlineformset_factory(
                get_user_model(), 
                Customer,
                fields=('email', 'first_name','last_name', 'address1', 
                         'phone_number', 'country', ),
                min_num=2,  # minimum number of forms that must be filled in
                extra=1,  # number of empty forms to display
                can_delete=False  # show a checkbox in each form to delete the row
)