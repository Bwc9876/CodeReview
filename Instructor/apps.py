"""
    This file provides configuration data to Django about this app
"""

from django.apps import AppConfig


class InstructorConfig(AppConfig):
    """
        This class defines configuration data for the Instructor app
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Instructor'
