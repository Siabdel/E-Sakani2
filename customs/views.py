from django.urls import reverse_lazy
from django.views import generic

from .forms import AccountUserCreationForm


class SignUp(generic.CreateView):
    form_class = AccountUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"
