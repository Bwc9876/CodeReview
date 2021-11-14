"""
    This file exposes the WSGI callable as a module-level variable named 'application'.
    It acts as the entrypoint of the site, we point the front-end webserver to this file
"""

import os

from django.core.wsgi import get_wsgi_application

from CodeReview.load_env import load_to_env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CodeReview.settings')
load_to_env('env.ps1')

application = get_wsgi_application()
