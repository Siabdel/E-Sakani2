import os
from PIL import Image
from django.shortcuts import render, get_object_or_404
from shop import models as sh_models
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    category = None
    categories = sh_models.Category.objects.all()
    products = sh_models.Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(sh_models.Category, slug=category_slug)
        products = sh_models.Product.objects.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'shop/product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(sh_models.Product, id=id, slug=slug, available=True)
     
    # Récupérer les images associées à ce produit en utilisant la méthode que nous avons définie dans le modèle
    product_images = product.images.all()

    cart_product_form = CartAddProductForm()
    context = {
        'product': product,
        'product_images' : product_images,
        'image' : product_images.first(),

        'cart_product_form': cart_product_form
    }
    return render(request, 'shop/product/detail.html', context)


def images_by_product_name(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        try:
            product = sh_models.Product.objects.get(name=product_name)
            images = sh_models.ProductImage.objects.filter(product=product)
        except sh_models.Product.DoesNotExist:
            images = None
    else:
        images = None
    return render(request, 'shop/product/images.html', {'image': images})

    
