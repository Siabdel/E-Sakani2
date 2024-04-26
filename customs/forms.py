from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm 
from customs.models import Custom
#
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Custom
        fields = ('email', 'first_name', 'last_name', 'company',
                  'address1', 'address2', 'country', 'phone_number',  )

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Custom
        fields = ('email', 'first_name', 'last_name', 'company',
                  'address1', 'address2', 'country', 'phone_number',  )