from django.urls import path, include
from . import views

from rest_framework import routers
from .api_views import *

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [

    # YOUR PATTERNS
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    path('api/', SpectacularSwaggerView.as_view(), name='swagger-ui'),

    # ReDoc at /api/doc/
    path('api/doc/', SpectacularRedocView.as_view(), name='doc'),



    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/short-urls/', ShortURLListAPIView.as_view(), name='short_url_list_api'),
    path('api/short-urls/<int:pk>', ShortURLUpdateAPIView.as_view(), name='short-url-update'),
    path('api/short-urls/<int:pk>/', ShortURLDeleteAPIView.as_view(), name='short-url-delete'),
    path('api/create-short-url/', ShortURLCreateAPIView.as_view(), name='create_short_url_api'),
    path('api/short-urls/<str:short_code>/', ShortURLRetrieveAPIView.as_view(), name='short-url-retrieve'),
    path('api/short-urls/locations/<str:short_code>/', UserLocationListAPIView.as_view(), name='user-location-list'),
    path('api/short-urls/locations/<str:short_code>/<int:pk>/', UserLocationRetrieveAPIView.as_view(), name='user-location-retrieve'),
    



    
    



    path('create/', views.create_short_url, name='create_short_url'),
    path('list/', views.short_url_list, name='short_url_list'),
    path('<str:short_code>/', views.redirect_short_url, name='redirect_short_url'),
    path('generate_qr_code/<str:short_code>/', views.generate_qr_code, name='generate_qr_code'),
    path('deactivate/<str:short_code>/', views.deactivate_short_url, name='deactivate_short_url'),
    path('edit/<str:short_code>/', views.edit_short_url, name='edit_short_url'),
    path('user_location_list/<str:short_code>/', views.user_location_list, name='user_location_list'),
    path('copy_to_clipboard/<str:short_code>/<int:location_id>/', views.copy_to_clipboard, name='copy_to_clipboard'),
    path('analysis/<str:short_code>/', views.analysis_view, name='analysis_view'),
    path('send_location/<str:short_code>/', views.send_location, name='send_location'),
]
