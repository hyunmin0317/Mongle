from django.urls import path, re_path
from django.views.static import serve
from pybo.views import list, list_detail, category, subway, seoul, covid19, bike

app_name = 'pybo'

urlpatterns = [
    # base_views.py
    path('list/', list, name='list'),
    path('list/<str:id>/', list_detail, name='list_detail'),
    path('category/<str:category>/', category, name='category'),

    # elastic.py
    path('subway/', subway, name='subway'),
    path('seoul/', seoul, name='seoul'),
    path('covid19/', covid19, name='covid19'),
    path('bike/', bike, name='bike'),
]