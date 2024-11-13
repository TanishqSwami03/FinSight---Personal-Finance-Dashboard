from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.contrib import  messages
from .models import *

from .utils import *
# Create your views here.

def dashboard(request):
    # Get the logged-in user
    user = request.user

    # Check if the user is authenticated
    if user.is_authenticated:
        # Get the user's wallet balance
        wallet_balance = user.wallet_balance

        # Get top stocks
        top_stocks = get_top_stocks()
        for stock in top_stocks:
            stock['change_class'] = 'text-success' if stock['percent_change'] >= 0 else 'text-danger'
            stock['icon_class'] = 'bi-caret-up-fill' if stock['percent_change'] >= 0 else 'bi-caret-down-fill'
            stock['percent_change'] = abs(stock['percent_change'])  # Calculate the absolute value here

        # Pass the user details to the template
        return render(request, 'dashboard.html', {
            'top_stocks': top_stocks,
            'user_name': user.first_name,  # Or user.username if you prefer
            'wallet_balance': wallet_balance,
        })

    else:
        return redirect('login')  # Redirect to login if not authenticated

def transaction(request):
    return render(request, 'transaction.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def wallet(request):
    user = request.user

    transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]  # Fetch last 5 transactions

    return render(request, 'wallet.html', {'user':user, 'transactions': transactions})

User = get_user_model()

def add_money(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
            if amount > 0:
                request.user.wallet_balance += amount
                request.user.save()
                
                # Create a transaction record
                Transaction.objects.create(user=request.user, transaction_type='add', amount=amount)
                
                messages.success(request, f"₹{amount:.2f} added to your wallet successfully!")
            else:
                messages.error(request, "Please enter a valid amount.")
        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid amount entered.")
    
    return redirect('wallet')

def calculator(request):
    return render(request, 'calculator.html')