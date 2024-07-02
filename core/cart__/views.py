# cart/views.py
from typing import Any
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from core.cart.cart import Cart
from core.cart.forms import CartAddProductForm
from core.utils import get_product_model
from shop import models as sh_models
from product import models as pro_models

## on charge le master models 
#product_model = get_product_model()
product_model = pro_models.Product

def cart_add_item(request, product_id):
    cart = Cart(request)  # create a new cart object passing it the request object 
    product = get_object_or_404(product_model, id=product_id) 
    cart.add(product=product,)
    return redirect('cart:cart_detail')

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)  # create a new cart object passing it the request object 
    product = get_object_or_404(Product_model, id=product_id) 
    form = CartAddProductForm(request.POST)

    
    if form.is_valid():
        cdata = form.cleaned_data
        cart.add(product=product, quantity=cdata['quantity'], update_quantity=True)
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product_model, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})

class CartCartItem(ListView): # new
    model = pro_models.Product
    template_name = "cart/detail.html"
    #context_object_name = "cart"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        
        context =  super().get_context_data(**kwargs)
        # cart
        moncart = sh_models.ShopCart.objects.get_or_create_cart(user=self.request.user)
        # items queryset
        items = sh_models.CartItem.objects.filter(cart=moncart)
        messages.add_message(self.request, messages.INFO, f"mes items dans panier {items}")
        
        # Ajouter le form pour chaque ligne du panier
        for item in items :
            initial_data = {'quantity': item.quantity, 'update': True}
            item.update_quantity_form = CartAddProductForm(initial=initial_data)
        context['cart'] = items
        return context