#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from PIL import Image
from product import models as pro_models
from django.conf import settings
from django.apps import apps

class DependencyError(Exception):
    def __init__(self, app_name):
        self._app_name = app_name

    def __str__(self):
        return u"A dependency is not satisfied: %s" % app_name

def check_dependency(app_name):
    if app_name not in settings.INSTALLED_APPS:
        raise DependencyError(app_name)

def clean_referer(request, default_referer='/'):
    """Returns the HTTP referer of the given <request>.

    If the HTTP referer is not recognizable, <default_referer> is returned.
    """
    referer = request.META.get('HTTP_REFERER', default_referer)
    return referer.replace("http://", "").replace("https://", "").replace(request.META['HTTP_HOST'], "")


def get_product_model():
    product_model_string = getattr(settings, 'CART_PRODUCT_MODEL', pro_models.Product)
    app_label, model_name = product_model_string.split('.')
    #raise Exception(f"model = {app_label} - {model_name}")

    return apps.get_model(app_label, model_name)

def process_resize_image(image, output_dir, thumbnail_size=(100, 100), large_size=(800, 600)):
    """
    Traite une images de produit en créant des miniatures de taille uniforme
    et une grande image.

    Args:
        image :  ProductImage instance
        output_dir (str): Le répertoire de sortie où les images traitées seront enregistrées.
        thumbnail_size (tuple): Taille de la miniature (largeur, hauteur). Par défaut: (100, 100).
        large_size (tuple): Taille de la grande image (largeur, hauteur). Par défaut: (800, 600).
    """

    # Ouvre l'image
    with Image.open(image.image.path) as img:
        # Crée une miniature
        thumbnail = img.copy()
        thumbnail.thumbnail(thumbnail_size)

        # Crée une grande image avec un rapport d'aspect préservé
        # Crée une grande image avec un rapport d'aspect préservé
        large_img = img.copy()
        large_img = large_img.resize(large_size)

        # Enregistre les images traitées
        base_name = os.path.basename(image.image.path)
        thumbnail_path = os.path.join(output_dir, 
                                  f"thumbnail_{thumbnail_size[0]}x{thumbnail_size[1]}_{base_name}")
        large_path = os.path.join(output_dir,
                                  f"large_{large_size[0]}x{large_size[1]}_{base_name}")

        thumbnail.save(thumbnail_path)
        large_img.save(large_path)

        # Retourne les chemins des images traitées
        return thumbnail_path, large_path


def process_product_images(product_id, output_dir, thumbnail_size=(100, 100), large_size=(800, 600)):
    """
    Traite les images de produit en créant des miniatures de taille uniforme
    et une grande image.

    Args:
        product_id (int): L'identifiant du produit.
        output_dir (str): Le répertoire de sortie où les images traitées seront enregistrées.
        thumbnail_size (tuple): Taille de la miniature (largeur, hauteur). Par défaut: (100, 100).
        large_size (tuple): Taille de la grande image (largeur, hauteur). Par défaut: (800, 600).
    """
    # Récupère les images du produit à partir du modèle ProductImage
    product_images = sh_models.ProductImage.objects.filter(product_id=product_id)

    # Parcourt chaque image du produit
    for image_obj in product_images:
        # Ouvre l'image
        with Image.open(image_obj.image.path) as img:
            # Crée une miniature
            thumbnail = img.copy()
            thumbnail.thumbnail(thumbnail_size)

            # Crée une grande image avec un rapport d'aspect préservé
            large_img = img.copy()
            large_img.thumbnail(large_size)

            # Enregistre les images traitées
            base_name = os.path.basename(image_obj.image.path)
            thumbnail_path = os.path.join(output_dir, f"thumbnail_{base_name}")
            large_path = os.path.join(output_dir, f"large_{base_name}")

            thumbnail.save(thumbnail_path)
            large_img.save(large_path)

            # Retourne les chemins des images traitées
            return thumbnail_path, large_path
