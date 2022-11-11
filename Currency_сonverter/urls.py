from django.contrib import admin
from django.urls import path, include
from django.urls import re_path as url

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', include('сonverter.urls')),
    path('registration/', include('users.urls')),
    path('blog/', include('blog.urls')),
        url(r'^', include('django.contrib.auth.urls')),
]
