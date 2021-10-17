import debug_toolbar

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("Main.urls")),
    path('users/', include('Users.urls')),
    path('instructor/', include("Instructor.urls")),
]

if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

handler404 = 'Main.views.error_404_handler'
handler403 = 'Main.views.error_403_handler'
handler500 = 'Main.views.error_500_handler'
