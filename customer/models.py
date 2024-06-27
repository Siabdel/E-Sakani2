from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField


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
        return f"{self.first_name} {self.last_name}"
# Client
class Customer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    company_logo = models.ImageField(blank=True)
    phone_number = PhoneNumberField(blank=True)
    
    class Meta:
        ordering = ('first_name', 'last_name', )
        verbose_name: "Customer"
        verbose_name_plural: "Customers"  # client 
        unique_together = ('email', )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse("client-detail", kwargs={"pk": self.pk})

    def __repr__(self):
        return f"Custom: {self.first_name} {self.last_name}"
