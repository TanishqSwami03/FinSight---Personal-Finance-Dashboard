from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/transaction/', transaction, name='transaction'),
    path('dashboard/portfolio/', portfolio, name='portfolio'),
    path('dashboard/wallet/', wallet, name='wallet'),
    path('dashboard/calculator/', calculator, name='calculator'),
]
