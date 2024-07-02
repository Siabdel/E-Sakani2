from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.views.generic import CreateView 
from customer.forms import AccountUserCreationForm, CustomFormSet
from django.db import transaction   
from shop.models import ShopCart
from django.conf import settings
from shop import models as sh_models
from customer import models as cli_models


class CustomCreate(CreateView):
    template_name = "customer/create_account_vuejs.html"
    form_class = AccountUserCreationForm
    success_url = '/shop/success/' # we will be redirected to
    
    def get_context_data(self, **kwargs):
        # author = get_object_or_404(User, pk=user_id)
        context = super(CustomCreate, self).get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = CustomFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = CustomFormSet(instance=self.object)
        return context
    
    def form_valid(self, form, formset): 
        # 
        with transaction.atomic():
            self.object = form.save(commit=False) # update username & save form
            self.object.username = self.object.email.split('@')[0]
            form.save()

            if formset.is_valid():
                formset.instance = self.object
                #client = formset.save(commit=False)
                formset.save()
                #
                # create invvoice 
                self.create_invoice(formset[0].cleaned_data)
                
        return super().form_valid(form)
     
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CustomFormSet(self.request.POST, self.request.FILES)

        # unique user
        v_email = self.request.POST['email']
        queryset =   User.objects.filter(email=v_email)
        """ 
        if  queryset.exists():
            messages.add_message(self.request, messages.INFO,
                             f" user exist ? = { v_email }")
            ##raise Exception("post formser = ", self.request.POST['email'])
            return self.form_invalid(form, formset)
        """

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)
        
    def form_invalid(self, form, formset):
        context = self.get_context_data(form=form, formset=formset)
        ##context['currentStep'] = 2
        return self.render_to_response(context)
    
    
class SignUp(CreateView):
    form_class = AccountUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"


class CustomCreate(CreateView):
    template_name = "customer/create_account_vuejs.html"
    form_class = AccountUserCreationForm
    success_url = '/shop/success/' # we will be redirected to
    
    def get_context_data(self, **kwargs):
        # author = get_object_or_404(User, pk=user_id)
        context = super(CustomCreate, self).get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = CustomFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = CustomFormSet(instance=self.object)
        return context
    
    def form_valid(self, form, formset): 
        # 
        with transaction.atomic():
            self.object = form.save(commit=False) # update username & save form
            self.object.username = self.object.email.split('@')[0]
            form.save()

            if formset.is_valid():
                formset.instance = self.object
                #client = formset.save(commit=False)
                formset.save()
                #
                # create invvoice 
                self.create_invoice(formset[0].cleaned_data)
                
        return super().form_valid(form)
     
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = CustomFormSet(self.request.POST, self.request.FILES)

        # unique user
        v_email = self.request.POST['email']
        queryset =   User.objects.filter(email=v_email)
        """ 
        if  queryset.exists():
            messages.add_message(self.request, messages.INFO,
                             f" user exist ? = { v_email }")
            ##raise Exception("post formser = ", self.request.POST['email'])
            return self.form_invalid(form, formset)
        """

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)
        
    def form_invalid(self, form, formset):
        context = self.get_context_data(form=form, formset=formset)
        ##context['currentStep'] = 2
        return self.render_to_response(context)
    
    def create_invoice(self, custom): 
        # cart 
        cart = Cart(self.request) 
        cart_id = self.request.session[settings.CART_SESSION_ID]
        shop_cart = sh_models.ShopCart.objects.get(id=cart_id)

        # 1- create invoice + ItemInvoice
        ## raise Exception("Customer.instance = ", custom.get('email'))
        email_client =  custom.get('email')
        client_obj = cli_models.Customer.objects.get(email=email_client)
        devis = inv_models.Invoice(title="Mon devis test", 
                                        author = self.request.user,
                                        client = client_obj, 
                                        invoice_total = 100,
                                        )
        items = shop_cart.item_articles.all()
        for item in items:
            article = item.content_type
            inv_models.InvoiceItem.objects.create(
                invoice = devis,
                item = article, 
                quantity = item.quantity,
                price = article.unit_price,
                rate = 12,
        )

"""
def create_invoice(self, custom): 
        # cart 
        cart = Cart(self.request) 
        cart_id = self.request.session[settings.CART_SESSION_ID]
        shop_cart = sh_models.ShopCart.objects.get(id=cart_id)

        # 1- create invoice + ItemInvoice
        ## raise Exception("Customer.instance = ", custom.get('email'))
        email_client =  custom.get('email')
        client_obj = cli_models.Customer.objects.get(email=email_client)
        devis = inv_models.Invoice(title="Mon devis test", 
                                        author = self.request.user,
                                        client = client_obj, 
                                        invoice_total = 100,
                                        )
        items = shop_cart.item_articles.all()
        for item in items:
            article = item.content_type
            inv_models.InvoiceItem.objects.create(
                invoice = devis,
                item = article, 
                quantity = item.quantity,
                price = article.unit_price,
                rate = 12,
        )
"""

