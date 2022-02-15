from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from config import settings
from pybo.views import base_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', base_views.home, name='home'),
    path('mongta/', include('pybo.urls')),
    path('common/', include('common.urls')),
    re_path(r'^static/(?P<path>.*)', serve, kwargs={'insecure': True})
]