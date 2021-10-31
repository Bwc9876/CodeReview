import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STAGE = os.getenv("DEV_STAGE", "Dev")

DEBUG = STAGE != "Prod"

SECRET_KEY = 'django-insecure-1&=3d#^^j*!8)r5y8tuh(t#rp6*(jwbx%90k-ir5c*2j4$s$o%' if DEBUG else os.getenv("SECRET_KEY")

ALLOWED_HOSTS = ['*'] if DEBUG else [os.getenv("PRODUCTION_HOST")]

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

WSGI_APPLICATION = 'CodeReview.wsgi.application'

if STAGE == "GH_TEST":
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
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

AUTHENTICATION_BACKENDS = [
    'Users.ldap_auth.LDAPAuthentication',
    'django.contrib.auth.backends.ModelBackend',
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
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'debug-emails'
else:
    EMAIL_BACKEND = "mailer.backend.DbBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_HOST_USER = os.getenv("EMAIL_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS", "")

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = False

USE_L10N = False

USE_TZ = False

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1'
    ]
    import mimetypes

    mimetypes.add_type("text/javascript", '.js')
