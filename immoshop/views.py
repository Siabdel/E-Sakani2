
# immoshop/views.py
from typing import Any
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from core.utils import get_product_model 
from cart.forms import CartAddProductForm
from product import models as pro_models
from core.taxonomy import models as tax_models

# product Model setting
product_model = get_product_model()

def category_list(request, catalog_slug=None ):
    category = get_object_or_404(category, slug=catalog_slug)
    products = Product.objects.filter(
        category__in = Categorie.objects.get(name=category_slug).get_descendants(include_self=False)
    )
    

def product_list(request, category_slug=None):
    category = None
    categories = tax_models.Category.objects.all()
    products = pro_models.Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(tax_models.Category, slug=category_slug)
        products = pro_models.Product.objects.filter(category=category)

    pro_context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, "immoshop/product_detail.html", context=pro_context)

@login_required
def product_immo_list(request, category_slug=None):
    products_list = product_model.objects.all()
    category = None
    categories = tax_models.Category.objects.all()
    #
    if category_slug:
        category = get_object_or_404(tax_models.Category, slug=category_slug)
    
    context = { 'products' : products_list,
                'category': category,
                'categories': categories,
                'cart_product_form' : CartAddProductForm()
               } 
    return render(request, "immoshop/product_list.html", context=context)

def product_immo_detail(request, product_id, slug):
    return render(request, "immoshop/product_detail.html", context={})

class ProductDetailView(DetailView): # new
    model = pro_models.ImmoProduct
    template_name = "immoshop/product_detail.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        
        context =  super().get_context_data(**kwargs)
        # formulaire 
        cart_product_form = CartAddProductForm()
        # Récupérer les images associées à ce produit en utilisant la méthode que nous avons définie dans le modèle
        product_images = self.get_object().images.all()

        context = {
            'product': self.get_object(),
            'product_images' : product_images,
            'image' : product_images.first(),
            'cart_product_form': cart_product_form
        }
      
        return context