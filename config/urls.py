from django.contrib import admin
from django.urls import path, include
from pybo.views import base_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', base_views.list, name='home'),
    path('mongta/', include('pybo.urls')),
    path('common/', include('common.urls')),
]