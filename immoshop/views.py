
# immoshop/views.py
from typing import Any
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from immoshop import models as msh_models



@login_required
def product_immo_list(request):
    products_list = msh_models.ImmoProduct.objects.all()
    context = {'products' : products_list} 
    return render(request, "immoshop/product_list.html", context=context)

def product_immo_detail(request, product_id, slug):
    return render(request, "immoshop/product_detail.html", context={})

class ProductDetailView(DetailView): # new
    model = msh_models.ImmoProduct
    template_name = "immoshop/product_detail.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        
        context =  super().get_context_data(**kwargs)
           
        # Récupérer les images associées à ce produit en utilisant la méthode que nous avons définie dans le modèle
        product_images = self.get_object().images.all()

        context['product_images'] = product_images
        return context