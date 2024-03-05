# -*- coding:UTF-8 -*-
import datetime
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.models import User, AnonymousUser
import math
from product import models as pro_models
from shop import models as sh_models
from shop.utils import get_product_model
from django.contrib.auth.models import AnonymousUser

class Cart(object):
    def __init__(self, request, product_model=None):
        self.session = request.session
        self.request = request
        self.cart = self.session[settings.CART_SESSION_ID] = {}
        #raise Exception(f"Model == { self.product_model }")
        # 1. user enregistre
            # 1.1 pas connecter 
                # voir si cart in session
                # sinon get or creer un cart 
            # 1.2 user connecter
                # sinon get or creer un cart 
        # 2. user AnonymousUser 
                # creer un cart 

        # 3. pas de User
        #
        self.cart = self.session.get(settings.CART_SESSION_ID)
        
        self.product_model = product_model if product_model else get_product_model()
        # on trouve un dans la session            
        if self.cart and request.user != AnonymousUser():
            try :
                self.cart = sh_models.ShopCart.objects.get_or_create_cart(request.user)
            except Exception as err: 
                self.cart = self.new(request)
        else :
            self.cart = self.session[settings.CART_SESSION_ID] = {}
            ##self.cart = self.new(request)
    

    def __iter__(self):
        for item in self.cart.item_set.all():
            yield item

    def new(self, request):
        cart = sh_models.ShopCart.objects.create(creation_date=datetime.datetime.now(), created_by = self.request.user)
        cart.save()
        request.session[settings.CART_SESSION_ID] = cart.id
        messages.add_message(self.request, messages.INFO, 'on cree un panier .%s' % cart.id)
        return cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        product = self.product_model.objects.get(pk=product_id)  # Remplacez YourProductModel par le modèle de produit approprié
        
        # Vérifiez si un article pour ce produit existe déjà dans le panier
        try:
            item, created = sh_models.ItemArticle.objects.get_or_create(
            cart=self.cart,
            product=product,
            defaults={'quantity': 1, 'unit_price': product.price}
            )
        
            if update_quantity:
                item.quantity = quantity
            else:
                item.quantity += quantity
            #
            item.save()
                
        except Exception as e:
             print("Une erreur s'est produite lors de la création de l'élément :", e)
        
        ##  Save In Session
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = pro_models.Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
