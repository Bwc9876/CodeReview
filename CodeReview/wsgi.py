"""
    This file exposes the WSGI callable as a module-level variable named 'application'.
    It acts as the entrypoint of the site, we point the front-end webserver to this file
"""

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

load_dotenv()

application = get_wsgi_application()
