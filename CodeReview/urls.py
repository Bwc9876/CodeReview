"""
    This file defines how urls map to views and other apps
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("Main.urls")),
    path('users/', include('Users.urls')),
    path('instructor/', include("Instructor.urls")),
]

# If we're debugging, we add paths for django's admin system and the debug toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

# This block defines what views to use in the event of an error
handler404 = 'Main.views.error_404_handler'  # Page Not Found
handler403 = 'Main.views.error_403_handler'  # Access Denied
handler500 = 'Main.views.error_500_handler'  # Internal Server Error
