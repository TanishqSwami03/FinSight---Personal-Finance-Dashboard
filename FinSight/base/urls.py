from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('login/', login, name='login'),
    path('logout/', logout_user, name='logout'),
    path('forgot-login-password/', forgot_login_password, name='forgot-login-password'),
    path('signup/', signup, name='signup'),
    path('signup-success/', signup_success, name='signup-success'),
]
