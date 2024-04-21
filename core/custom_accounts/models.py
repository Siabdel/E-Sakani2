from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    company_logo = models.ImageField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True, default="")
    
    class Meta(AbstractUser.Meta):
         swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return f"{self.username}"