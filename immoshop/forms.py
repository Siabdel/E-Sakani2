
from django import forms
from customs.models import CustomUser, Custom
from customs.forms import CustomCreatForm
from django.contrib.auth import get_user_model



class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

CustomFormSet = forms.inlineformset_factory(
                get_user_model(), 
                Custom, 
                form = CustomCreatForm, 
                extra=1
                )