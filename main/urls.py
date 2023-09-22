# Description: This file contains the URL patterns for the main app

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('location.urls')),
    path('', include('short_link.urls')),

]

