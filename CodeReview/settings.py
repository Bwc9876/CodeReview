"""
    This file defines the settings for this project.
"""

import os
from pathlib import Path

# This option defines what folder is the root of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# This option isn't part of the django framework, but it defines what stage of development we're in
# Options are:
# Dev: We're debugging the project
# GH_TEST: We're in GitHub running tests
# Prod: We're in production and actively serving the site
STAGE = os.getenv("DEV_STAGE", "Dev")

# This option defines if we're debugging, it's used to determine many aspects of the project
DEBUG = STAGE != "Prod"

# This option is used in encryption, if we're debugging, we don't care that people know what it is
# But, if we're in Production, we'll load the key from the environment
SECRET_KEY = 'django-insecure-1&=3d#^^j*!8)r5y8tuh(t#rp6*(jwbx%90k-ir5c*2j4$s$o%' if DEBUG else os.getenv("SECRET_KEY")

# This option defines what url someone can type in to access this site. If we're debugging, it doesn't matter
# But, in production we want to only let a specific url be used, so we load it from the environment
ALLOWED_HOSTS = ['*'] if DEBUG else [os.getenv("PRODUCTION_HOST")]

# This option defines what apps to load
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mailer',
    'debug_toolbar',
    'Main',
    'Users',
    'Instructor',
]

# This option defines what middleware is run on a request, middleware is run before any view logic is executed
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

# This option defines what urls.py file to use for urls
ROOT_URLCONF = 'CodeReview.urls'

# This option defines how templates are rendered
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

# This next block of code defines how our database will work and what database system will work
if STAGE == "Prod":
    # In production, we use MySQl as our database backend
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
            'NAME': 'github_actions',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
else:
    # In development, we use an sqlite3 database file as the database backend
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# This option defines what password validation functions to use
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

# This option defines what backends we use for authentication
if DEBUG:
    AUTHENTICATION_BACKENDS = [
        'Users.ldap_auth.LDAPAuthentication',
        'django.contrib.auth.backends.ModelBackend',
    ]
else:
    AUTHENTICATION_BACKENDS = [
        'Users.ldap_auth.LDAPAuthentication',
    ]

# This option defines what Model to use in Auth backend for storing user data
AUTH_USER_MODEL = "Users.User"

# This option defines what url to go when the user is not logged in
LOGIN_URL = "/users/login"

# This option defines what url to go to after the user has logged in
LOGIN_REDIRECT_URL = "/"

# This option defines what url to go to after logging out
LOGOUT_REDIRECT_URL = "/users/logout-done"

# LDAP AUTH

# This setting denotes what url to use to access the LDAP server
LDAP_URL = os.getenv('LDAP_URL', "localhost")
# This setting tells ldap what NetBIOS domain name to use when logging in a user
LDAP_DOMAIN = os.getenv('LDAP_DOMAIN', None)
# This setting tells ldap what base search context to use when searching for a user
LDAP_BASE_CONTEXT = os.getenv('LDAP_BASE_CONTEXT', None)

# This next block of code defines how emails will work
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

# This option defines what language code django will send to browsers
LANGUAGE_CODE = 'en-us'

# This option defines what timezone the server is in
TIME_ZONE = 'EST'

# These options relate to localization, but, since this is an intranet site we don't need it.
USE_I18N = False
USE_L10N = False
USE_TZ = False

# These options define urls for static urls
STATIC_URL = '/static/'
STATIC_ROOT = os.getenv("STATIC_DIR", "collected-static")

# This option defines which field to use automatically for PrimaryKeys
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if not DEBUG:
    # If we're in production, all messages will go to a local file named "django_log.txt"
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
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': True,
            },
        },
    }

# This next block of code initializes django-debug-toolbar if we're debugging
if DEBUG:
    # This option defines which IPs the toolbar will display on
    INTERNAL_IPS = [
        '127.0.0.1'
    ]

    # This next block of code tackles a strange issue where windows doesn't set JS mimetypes to 'text/javascript'
    # This causes the browser to incorrectly load the JavaScript
    import mimetypes
    mimetypes.add_type("text/javascript", '.js')
