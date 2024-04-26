
from django import forms
from customs.models import CustomUser 

class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
