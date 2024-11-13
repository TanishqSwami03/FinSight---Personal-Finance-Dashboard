from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/transaction/', transaction, name='transaction'),
    path('dashboard/portfolio/', portfolio, name='portfolio'),
    path('dashboard/wallet/', wallet, name='wallet'),
    path('add_money/', add_money, name='add_money'),
    path('dashboard/calculator/', calculator, name='calculator'),
]
