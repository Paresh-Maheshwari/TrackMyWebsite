from django.urls import path
from .views import *
from .authentication import *


urlpatterns = [
    path('',home,name='home'),
    path("contact/",contact,name='contact'),
    path("location/<token>/", send_location, name="send_location"),
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path('logout/', logoutaccount,name='logoutaccount'),
    path('user_track/', user_track, name='user_track'),
    path('token_summary/', token_summary, name='token_summary'),
    path('download/excel', export_excel, name='export_excel'),
    path('download/csv/', export_csv, name='export_csv'),
    path('download/json/', export_json, name='export_json'),
    path('verify/<str:code>', verify, name='verify'),
    path('resend_verification/', resend_verification, name='resend_verification'),
    path('forgot/', forgot_password, name='forgot_password'),
    path('reset/<str:reset_code>/', reset_password, name='reset_password'),
]
