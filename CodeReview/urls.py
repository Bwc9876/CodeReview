import debug_toolbar

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("Main.urls")),
    path('users/', include('Users.urls'))
]

if settings.DEBUG:
    urlpatterns.append(path('admin/', admin.site.urls))
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
