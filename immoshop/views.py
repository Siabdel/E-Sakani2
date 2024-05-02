
# Dajango Contrib
from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils.decorators import method_decorator
## Generic View
from django.views.generic import (
    View,
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views import View
## local app modules
from weasyprint import HTML
from core.orders.models import OrderItem
from core.product import models as pro_models
from core.shop import models as sh_models 
from immoshop import models as immo_models
from invoices import models as devis_models
from core.cart.cart import Cart
from django.urls import reverse, resolve
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from customs.forms import CustomCreatForm, AccountUserCreationForm
from core.utils import get_product_model, Dict2Obj
from core.cart.forms import CartAddProductForm
from core.taxonomy import models as tax_models


# product Model setting
product_model = get_product_model()

def category_list(request, categoy_slug=None ):
    category = get_object_or_404(pro_models.MPCategory, slug=categoy_slug)
    products = pro_models.ImmoProduct.objects.filter(
        category__in = pro_models.MPCategory.objects
        .get(name=categoy_slug).get_descendants(include_self=False)
    )
    context = {
            "categoy": category,
            "products": products,
            }
    return render(request, "immoshop/category_list.html", context=context)
    

def product_list(request, category_slug=None):
    category = None
    categories = pro_models.MPCategory.objects.all()
    products = pro_models.Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(pro_models.MPCategory, slug=category_slug)
        products = pro_models.Product.objects.filter(category=category)

    pro_context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, "immoshop/product_detail.html", context=pro_context)

def product_home(request, category_slug=None):
    products_list = product_model.objects.all()
    category = None
    categories = pro_models.MPCategory.objects.all()
    #
    if category_slug:
        category = get_object_or_404(pro_models.MPCategory, slug=category_slug)
    
    # ProductSpecificationValues
    for product in products_list:
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
    
    context = { 'products' : products_list,
                'category': category,
                'categories': categories,
                'cart_product_form' : CartAddProductForm()
               } 
    return render(request, "immoshop/home.html", context=context)

@login_required
def product_immo_list(request, category_slug=None):
    products_list = product_model.objects.all()
    category = None
    categories = pro_models.MPCategory.objects.all()
    #
    if category_slug:
        category = get_object_or_404(pro_models.MPCategory, slug=category_slug)
    
    context = { 'products' : products_list,
                'category': category,
                'categories': categories,
                'cart_product_form' : CartAddProductForm()
               } 
    return render(request, "immoshop/product_list.html", context=context)

def product_immo_detail(request, product_id, slug):
    return render(request, "immoshop/product_detail.html", context={})

class ProductDetailView(DetailView): # new
    model = immo_models.ImmoProduct
    template_name = "immoshop/product_detail.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        
        context =  super().get_context_data(**kwargs)
        # formulaire 
        cart_product_form = CartAddProductForm()
        # Récupérer les images associées à ce produit en utilisant la méthode que nous avons définie dans le modèle
        product = self.get_object()
        product_images = product.images.all()
        # les psecifications du produit 
        
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
            'cart_product_form': cart_product_form
        }
      
        return context
    
class AccompteUserCreate(View):
    template_name = "immoshop/create.html"
    form_class = AccountUserCreationForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        # formulaire 
        account_form = self.form_class()
        context = context.upoadet({
            'form': account_form
        })
        return context
        
    def get(self, request):
        #
        form = self.form_class(initial={"user": request.user})
        return render(request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        # cart 
        cart = Cart(request) 
        cart_id = request.session[settings.CART_SESSION_ID]

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.instance
            form.save()
            ## url = reverse('invoice-detail', kwargs={'pk' : devis.pk}) 
            #response =  redirect('invoice:invoice-detail')
            return redirect('immoshop:invoice_create', user_id=user.pk)

        return render(request, self.template_name, {"form": form})
    
    
    
class InvoiceCreate(View):
    template_name = "immoshop/create.html"
    form_class = CustomCreatForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        # formulaire 
        custom_form = self.form_class()
        context = context.upoadet({
            'form': custom_form
        })
      
        return context
        
    def get(self, request, user_id):
        #
        user = User.objects.get(pk=user_id)
        form = self.form_class(initial={"user": user})
        ## 
        return render(request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        # cart 
        cart = Cart(request) 
        cart_id = request.session[settings.CART_SESSION_ID]

        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            shop_cart = sh_models.ShopCart.objects.get(id=cart_id)
            items = shop_cart.item_articles.all()
            # 1- create client 
            form.instance.user = request.user
            customer  = form.save()
            
            # 2- create invoice + ItemInvoice
            devis = devis_models.Invoice(title="Mon devis test", 
                                         client = customer, 
                                         invoice_total = 100,
                                         )
            for item in items:
                devis_models.InvoiceItem.objects.create(
                    invoice = devis,
                    item = item, 
                    quantity=item.quantity,
                    rate = 12,
                    tax = 15.5, 
                    price=item.product.price,
                )
            # vider le panier 
            cart.clear()
            
            ## url = reverse('invoice-detail', kwargs={'pk' : devis.pk}) 
            #response =  redirect('invoice:invoice-detail')
            return redirect('invoice_detail', pk=devis.pk)
        else :
            user = form.instance.user
            #return redirect('invoice_create', user_id=user.pk)
            return render(request, self.template_name, {"form": form})
    
    
    
def invoice_create(request):
    """ 
    1- create client user
    2- create invoice + ItemInvoice
    3- Valider la commande ou la reservation
    """
    cart = Cart(request) 
    cart_id = request.session[settings.CART_SESSION_ID]
    #raise Exception(f" cart={cart}, card_id={cart_id}")
    context = {} 
    shop_cart = sh_models.ShopCart.objects.get(id=cart_id)
    items = shop_cart.item_articles.all()
    
    if request.method == 'POST':
        form = CustomCreatForm(request.POST)
        if form.is_valid():
            # 1- create client 
            customer  = form.save()
            # 2- create invoice + ItemInvoice
            devis = devis_models.Invoice(title="Mon devis test", 
                                         client = customer, 
                                         invoice_total = 100,
                                         )
            for item in items:
                devis_models.InvoiceItem.objects.create(
                    invoice = devis,
                    item = item, 
                    quantity=item.quantity,
                    rate = 12,
                    tax = 15.5, 
                    price=item.product.price,
                )
            # vider le panier 
            cart.clear()
            ## url = reverse('invoice-detail', kwargs={'pk' : devis.pk}) 
            #response =  redirect('invoice:invoice-detail')
            return redirect('invoice_detail', pk=devis.pk)
    else:
        form = CustomCreatForm()
        context = { 'items':items, 'form': form }

    return render(request, 'orders/order/create.html', context )

        
@login_required
def generate_pdf_invoice(request, invoice_id):
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


class AccompteUserCreate(View):
    form_class = AccountUserCreationForm
    template_name = "immoshop/create.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        # formulaire 
        account_form = self.form_class()
        context = context.upoadet({
            'form': account_form
        })
        return context
        
    def get(self, request):
        #
        form = self.form_class(initial={"user": request.user})
        return render(request, self.template_name, {"form": form})
    
    def post(self, request, *args, **kwargs):
        # cart 
        cart = Cart(request) 
        cart_id = request.session[settings.CART_SESSION_ID]

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.instance
            form.save()
            ## url = reverse('invoice-detail', kwargs={'pk' : devis.pk}) 
            #response =  redirect('invoice:invoice-detail')
            return redirect('immoshop:invoice_create', user_id=user.pk)

        return render(request, self.template_name, {"form": form})
    
    

from immoshop.forms import CustomFormSet
from customs.forms import CustomCreatForm, AccountUserCreationForm
class CreateAccount(View) :
    template_name = "immoshop/create_account_vuejs.html"
    form_class = AccountUserCreationForm
    currentPage = 1

    def get(self, request):
        account_form = AccountUserCreationForm()
        custom_formset = CustomFormSet()
        context = {
            'account_form': account_form, 
            'custom_formset': custom_formset,
            'currentPage' : self.currentPage ,
            }
        
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        account_form = AccountUserCreationForm(request.POST)
        custom_formset = CustomFormSet(request.POST)

        if account_form.is_valid() and custom_formset.is_valid():
            custom_formset.instance = account_form.save()
            custom_formset.save()
            return redirect('success_url')

        elif not custom_formset.is_valid(): 
            self.currentPage = 2
        else : 
            self.currentPage = 1
  
        context = {
            'account_form': account_form, 
            'custom_formset': custom_formset,
            'currentPage' : self.currentPage,
        }
        return render(request, self.template_name, context=context)

   

def success(request):
    return render(request, 'success.html')

