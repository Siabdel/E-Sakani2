
from django import forms
from customs.models import CustomUser, Custom
from customs.forms import CustomCreatForm
from django.contrib.auth import get_user_model



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
        model = Custom
        fields = "__all__" 

CustomFormSet = forms.inlineformset_factory(
                get_user_model(), 
                Custom,
                fields=('email', 'first_name','last_name', 'address1', 
                         'phone_number', 'country', ),
                min_num=2,  # minimum number of forms that must be filled in
                extra=1,  # number of empty forms to display
                can_delete=False  # show a checkbox in each form to delete the row
)