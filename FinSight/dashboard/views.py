from django.shortcuts import render

from .utils import *
# Create your views here.

def dashboard(request):
    # top stocks
    top_stocks = get_top_stocks()
    for stock in top_stocks:
        stock['change_class'] = 'text-success' if stock['percent_change'] >= 0 else 'text-danger'
        stock['icon_class'] = 'bi-caret-up-fill' if stock['percent_change'] >= 0 else 'bi-caret-down-fill'
        stock['percent_change'] = abs(stock['percent_change'])  # Calculate the absolute value here


    return render(request, 'dashboard.html', {'top_stocks' : top_stocks})

def transaction(request):
    return render(request, 'transaction.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def wallet(request):
    return render(request, 'wallet.html')

def calculator(request):
    return render(request, 'calculator.html')