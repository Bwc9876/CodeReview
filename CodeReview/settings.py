"""
    This file defines the settings for this project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# This option isn't part of the django framework, but it defines what stage of development we're in
# Options are:
# Dev: We're debugging the project
# GH_TEST: We're in GitHub running tests
# Prod: We're in production and actively serving the site
STAGE = os.getenv("DEV_STAGE", "Dev")

DEBUG = STAGE != "Prod"

# This option is used in encryption, if we're debugging, we don't care that people know what it is
# But, if we're in Production, we'll load the key from the environment
SECRET_KEY = 'django-insecure-1&=3d#^^j*!8)r5y8tuh(t#rp6*(jwbx%90k-ir5c*2j4$s$o%' if DEBUG else os.getenv("SECRET_KEY")

# This option defines what url someone can type in to access this site. If we're debugging, it doesn't matter
# But, in production we want to only let a specific url be used, so we load it from the environment
ALLOWED_HOSTS = ['*'] if DEBUG else [os.getenv("PRODUCTION_HOST")]
if os.getenv('CSRF_TRUSTED_ORIGINS', None) is not None:
  CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", '').split(';')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mailer',
    'Main',
    'Users',
    'Instructor',
]

if DEBUG:
    INSTALLED_APPS += [
        'django.contrib.admin',
        'debug_toolbar'
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG is False:
    MIDDLEWARE.pop(3)
    CSRF_FAILURE_VIEW = 'Main.views.csrf_failure_view'

ROOT_URLCONF = 'CodeReview.urls'

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
                'Main.context_processors.base_context',
            ],
            'debug': DEBUG
        },
    },
]

# This option defines what wsgi application to use in development when running the app through runserver
WSGI_APPLICATION = 'CodeReview.wsgi.application'

if STAGE == "Prod":
    # In production, we use MySQL as our database backend
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'CodeReview',
            'USER': os.getenv("DB_USERNAME", ""),
            'PASSWORD': os.getenv("DB_PASSWORD", ""),
            'HOST': os.getenv("DB_HOST", "localhost"),
            'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
        }
    }
elif STAGE == "GH_TEST":
    # In GitHub testing, we use Postgre as a database backend
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'GitHub_actions',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
else:
    # In development, we use an SQLITE3 database file as the database backend
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

if DEBUG:
    # If we're in development, we add django's model backend so that way we can debug
    AUTHENTICATION_BACKENDS = [
        'Users.ldap_auth.LDAPAuthentication',
        'django.contrib.auth.backends.ModelBackend',
    ]
else:
    # If we're in production, we only want to allow authentication through LDAP
    AUTHENTICATION_BACKENDS = [
        'Users.ldap_auth.LDAPAuthentication',
    ]

AUTH_USER_MODEL = "Users.User"

LOGIN_URL = "/users/login"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/users/logout-done"

# LDAP AUTH

LDAP_URL = os.getenv('LDAP_URL', "localhost")
LDAP_DOMAIN = os.getenv('LDAP_DOMAIN', None)
LDAP_BASE_CONTEXT = os.getenv('LDAP_BASE_CONTEXT', None)

if DEBUG:
    # If we're debugging, we never actually send any emails, we just save what they would be as text files
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'debug-emails'
    EMAIL_DOMAIN = "example.com"
    EMAIL_ADMIN_DOMAIN = "admin.example.com"
else:
    # If we're not debugging, we use django-mailer to send emails
    EMAIL_BACKEND = "mailer.backend.DbBackend"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_HOST_USER = os.getenv("EMAIL_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS", "")
    EMAIL_DOMAIN = os.getenv("EMAIL_DOMAIN", "")
    EMAIL_ADMIN_DOMAIN = os.getenv("EMAIL_ADMIN_DOMAIN", "")
    SERVER_EMAIL = EMAIL_HOST_USER
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

# These options relate to localization, but, since this is an intranet site we don't need it.
USE_I18N = False
USE_L10N = False
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv("STATIC_DIR", "collected-static")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG is False:
    # If we're in production, all messages will go to a local file named "django_logs.txt"
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': 'django_logs.txt',
            },
        },
        'root': {
            'handlers': ['file'],
            'level': 'WARNING'
        }
    }

if os.getenv("SECURITY", "NONE") == "SECURE":
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 604800
    SECURE_SSL_REDIRECT = True

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1'
    ]

    # This next block of code tackles a strange issue where windows doesn't set JS mimetypes to 'text/javascript'
    # This causes the browser to incorrectly load the JavaScript
    import mimetypes

    mimetypes.add_type("text/javascript", '.js')
