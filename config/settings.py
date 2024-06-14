"""
Django settings for django project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from pathlib import Path
# import des variables projects
from config.projects import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent
# Directory project au meme niveau de settings.py
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
SHOP_APP_LABEL = 'myshop'
APP_LABEL = 'myshop'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jf$ac236s)uv)6xa&o0#@wmt+37zvlwf=atbi)%et^7=%3#$bb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Application definition

INSTALLED_APPS = [
    'mptt',
    'core.product', # Product
    'core.taxonomy', # new
    'core.profile',  # new
    'core.orders', # Orders
    'core.shop', # Shop
    'core.cart', # Cart
    'core.mfilesupload', # Multi files upload
    #'core.custom_accounts.apps.AccountsConfig',
    'project', # new
    'polymorphic',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # new
    # debug tools
    'debug_toolbar', # new
    'corsheaders', 
    # User Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Third party
    "crispy_forms",
    "crispy_bootstrap4",
    "django_extensions",
    #'markdownx', # <-- needed for adding markdown to forms
    # local app
    'mapwidgets', ## new google map
    'immoshop.apps.ImmoShopConfig', # Cart
    "invoices",
    'customs', # custom
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",  # new
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add the account middleware:
    "allauth.account.middleware.AccountMiddleware",
    # debug 
    'debug_toolbar.middleware.DebugToolbarMiddleware', # new
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.cart.context_processors.cart', ## new
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'



# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CART_PRODUCT_MODEL = 'immoshop.ImmoProduct'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'Fr-fr'

DEFAULT_CHARSET='UTF-8'

TIME_ZONE = 'UTC'
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
# Lorsque USE_TZ vaut True et que la base de données ne gère pas les fuseaux horaires (par ex. SQLite, MySQL, Oracle), Django lit et écrit les dates/heures en heure locale en fonction de cette option quand elle est définie et en UTC si elle ne l’est pas.

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static" )
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
    os.path.join(BASE_DIR, 'media'),
    os.path.join(BASE_DIR, 'media', 'upload'),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'



CART_SESSION_ID = 'CARD_ID'

# Image resize 
DJANGORESIZED_DEFAULT_SIZE = [1920, 1080]
DJANGORESIZED_DEFAULT_SCALE = 0.5
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

## 

FILE_UPLOAD_MAX_MEMORY_SIZE = 20 # 2621440 (c-à-d. 2.5 Mio).



## BLOG MDEDITOR ##
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Map settings
GOOGLE_MAP_API_KEY = "<key>"
MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocationName", "amsterdam"),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'nl'}}),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": GOOGLE_MAP_API_KEY
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : [
        ##'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTIFICATION_CLASS' : [
        'rest_famework.authentification.SessionAuthentification', 
        'rest_framework.authentification.BasicAuthentification',
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
        'rest_framework.authtoken',
    ] 
    
}


# Securite API corsheaders

CORS_ORIGIN_ALLOW_ALL = True # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    "http://localhost:8000",
    'http://localhost:8080',
] # If this is used, then not need to use `CORS_ORIGIN_ALLOW_ALL = True`
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8080',
]

LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/login/"