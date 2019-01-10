"""
Django settings for recepcao project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm%!)6=)=n!=sgt5$_r=a=rw5sg$qto^75hn5rr6lic14=r7al_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

CUSTOM_APPS = [
    "rest_framework",
    "app"
]

INSTALLED_APPS = DEFAULT_APPS + CUSTOM_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recepcao.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'recepcao.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# Armazenar arquivos upados
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)

if not os.path.isdir(MEDIA_ROOT):
    print("media folder nonexistent. creating %s ..." % MEDIA_ROOT)
    os.mkdir(MEDIA_ROOT)

# Onde procurar o arquivo IPC para conectar-se ao node rodando
IPC_PATH = "/home/diego/projetos/ethereum/redeprivada/geth.ipc"

# Onde procurar o arquivo *.abi que descreve o contrato
ABI_PATH = "/home/diego/projetos/ferias2018.2/blockchain/Blockchain.abi"

if not os.path.isfile(ABI_PATH):
    print("Aviso: não foi encontrado um arquivo ABI que descreve o contrato no ABI_PATH %s" % ABI_PATH)


# Endereço que essa aplicação usa para se identificar na rede ethereum
ENDERECO_ETH = "0x39eE1AaDa22070410068749e398F2e29128Dda79"
# Endereço do contrato que gerencia o saldo
ENDERECO_CONTRATO_ETH = "0xBCd0Cc1Ab94D632780Ef5E4bCb03038B396f7668"
# Passphrase para autenticar-se no nó geth
PASSPHRASE_ETH = "recepcao"