
# product/views.py
from typing import Any
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, CreateView
from core.utils import get_product_model, Dict2Obj
from product import models as pro_models
from shop import models as msh_models 
from product import models as pro_models
from django.conf import settings
from .forms import CartAddProductForm
from .models import ShopCart

# product Model setting
product_model = get_product_model()
class ProductDetailView(DetailView): # new
    model = pro_models.Product
    template_name = "product/product_detail.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        
        context =  super().get_context_data(**kwargs)
        # formulaire 
        cart_product_form = CartAddProductForm()
        # Récupérer les images associées à ce produit en utilisant la méthode que nous avons définie dans le modèle
        product = self.get_object()
        product_images = product.get_images()
        # les psecifications du produit 
        ## raise Exception("options = ", product.options)

        options = [] 
        psv = pro_models.ProductSpecificationValue.objects.filter(product=product)
        for spec in psv:
            attributes = {"product": spec.product.id,
                       "name": spec.specification.name,
                       "value": spec.value,
                    }
            options.append(Dict2Obj(attributes))
        ## add options
        product.options = options

        context = {
            'product':  product,
            'product_images' : product_images,
            'image' : product_images.first(),
            'cart_product_form': cart_product_form,
            'app_name' : 'carshop',
        }
      
        return context
    
def cart_add_one_item(request, product_id):
    cart = ShopCart.objects.get_or_create_cart(request.user)  # create a new cart object passing it the request object 
    product = get_object_or_404(product_model, id=product_id) 
    #raise Exception("j'ai panier et produit")
    cart.add_product(product=product,)
    return redirect('cart:cart_detail')
    

@require_POST
def cart_add_item(request, product_id):
    cart = ShopCart.objects.get_or_create_from_request(request)  # create a new cart object passing it the request object 
    product = get_object_or_404(pro_models.Product, id=product_id) 
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cdata = form.cleaned_data
        cart.add(product=product, quantity=cdata['quantity'], update_quantity=True)
    return redirect('cart:cart_detail')

def cart_remove_item(request, product_id):
    cart = ShopCart.objects.get_or_create_from_request(request)
    product = get_object_or_404(pro_models.Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = ShopCart.objects.get_or_create_from_request(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})


    """Generate PDF Invoice"""

    queryset = Invoice.objects.filter(user=request.user)
    invoice = get_object_or_404(queryset, pk=invoice_id)

    client = invoice.client
    user = invoice.user
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)

    context = {
        "invoice": invoice,
        "client": client,
        "user": user,
        "invoice_items": invoice_items,
        "host": request.get_host(),
    }
    print(request.get_host())

    html_template = render_to_string("pdf/html-invoice.html", context)

    pdf_file = HTML(
        string=html_template, base_url=request.build_absolute_uri()
    ).write_pdf()
    pdf_filename = f"invoice_{invoice.id}.pdf"
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = "filename=%s" % (pdf_filename)
    return response