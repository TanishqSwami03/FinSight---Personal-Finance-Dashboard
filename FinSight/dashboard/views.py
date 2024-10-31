from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def transaction(request):
    return render(request, 'transaction.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def wallet(request):
    return render(request, 'wallet.html')

def calculator(request):
    return render(request, 'calculator.html')