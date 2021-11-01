"""
    This file defines how our models interact with Django's admin interface
"""

from django.conf import settings
from django.contrib import admin

from . import models

# We'll be using our own system for Rubric creation in production, so we only run this in debug
if settings.DEBUG:
    admin.site.register(models.Rubric)
