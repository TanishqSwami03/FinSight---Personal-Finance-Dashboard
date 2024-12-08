from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/transaction/', transaction, name='transaction'),
    path('dashboard/portfolio/', portfolio, name='portfolio'),
    path('dashboard/wallet/', wallet, name='wallet'),
    path('add_money/', add_money, name='add_money'),
    path('send-money/', send_money, name='send_money'),
    path('receive_money/', receive_money, name='receive_money'),
    path('dashboard/calculator/', calculator, name='calculator'),
    path('company_shares/', company_shares, name = 'company_shares'),
    path('search_stock/', search_stock, name='search_stock'),
    path('buy_stock/', buy_stock, name='buy_stock'),
    path('get_stock_price/', get_stock_price, name='get_stock_price'),
    path('sell/', sell_stock, name='sell_stock'),
    path('mutual_funds/', mutual_funds, name='mutual_funds'),
    path('insights/', insights, name='insights'),
]
