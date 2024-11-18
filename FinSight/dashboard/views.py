from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.contrib import  messages
from django.db.models import Sum
from django.http import JsonResponse
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
     # Fetch all transactions from the database
    transactions = Transaction.objects.all().order_by('-date')  # Sort by date descending

    return render(request, 'transaction.html',{
        'transactions' : transactions
    })

def portfolio(request):
    return render(request, 'portfolio.html')

def wallet(request):
    user = request.user

    # Get the total income and total expense for the logged-in user
    total_income = Transaction.objects.filter(user=request.user, transaction_type='receive').aggregate(total_income=Sum('amount'))['total_income'] or Decimal(0)
    total_expense = Transaction.objects.filter(user=request.user, transaction_type='send').aggregate(total_expense=Sum('amount'))['total_expense'] or Decimal(0)

    transactions = Transaction.objects.filter(user=user).order_by('-date')[:6]  # Fetch last 5 transactions

    return render(request, 'wallet.html', {
        'user':user, 
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        }
    )

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

def send_money(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        contact = request.POST.get('contact')

        if amount > request.user.wallet_balance:
            messages.error(request, "Insufficient balance.")
            return redirect('wallet')

        # Deduct the amount from the user’s wallet
        request.user.wallet_balance -= amount
        request.user.save()

        # Log the transaction
        Transaction.objects.create(
            user=request.user,
            transaction_type='send',
            amount=amount
        )

        messages.success(request, f"Successfully sent ₹{amount} to {contact}.")
        return redirect('wallet')
    return redirect('wallet')

def receive_money(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        contact = request.POST.get('contact')  # Random sender name, no checking needed

        if amount <= 0:
            messages.error(request, "Invalid amount.")
            return redirect('wallet')

        # Update the wallet balance
        user = request.user
        user.wallet_balance += amount
        user.save()

        # Log the transaction for receiving money
        Transaction.objects.create(
            user=request.user,  # The logged-in user is the receiver
            transaction_type='receive',
            amount=amount
        )

        # You can add any other logic if necessary, like sending a notification to the sender.

        messages.success(request, f"Successfully received ₹{amount} from {contact}.")
        return redirect('wallet')

    return redirect('wallet')

def calculator(request):
    return render(request, 'calculator.html')

def company_shares(request):
    # Get top stocks
    top_stocks = get_top_stocks()
    for stock in top_stocks:
        stock['change_class'] = 'text-success' if stock['percent_change'] >= 0 else 'text-danger'
        stock['icon_class'] = 'bi-caret-up-fill' if stock['percent_change'] >= 0 else 'bi-caret-down-fill'
        stock['percent_change'] = abs(stock['percent_change'])

    # Fetch user portfolio
    user_portfolio = Portfolio.objects.filter(user=request.user)
    portfolio_data = []

    for portfolio in user_portfolio:
        try:
            # Fetch current price
            current_price_str = portfolio.get_current_price()  # Returns as string
            current_price = Decimal(current_price_str)  # Convert to Decimal for calculation
            
            # Calculate derived values
            average_price = portfolio.average_price
            invested_value = portfolio.invested_value
            profit = (current_price - average_price) * portfolio.quantity
            percentage_change = ((current_price - average_price) / average_price) * 100
            today_trend = "Bullish" if percentage_change > 0 else "Bearish"

            # Print for debugging
            print(f"Current Price: {current_price}, Average Price: {average_price}, Invested Value: {invested_value}")
            print(f"Profit: {profit}, Percentage Change: {percentage_change}, Trend: {today_trend}")

            # Add to portfolio data
            portfolio_data.append({
                "stock_symbol": portfolio.stock_symbol,
                "current_price": current_price,
                "average_price": average_price,
                "quantity": portfolio.quantity,
                "invested_value": invested_value,
                "percentage_change": percentage_change,
                "profit": profit,
                "today_trend": today_trend,
            })
        except Exception as e:
            print(f"Error processing stock {portfolio.stock_symbol}: {e}")

    return render(request, 'company_shares.html', {
        'top_stocks': top_stocks,
        'portfolios': portfolio_data,  # Pass processed portfolio data
    })

from django.http import JsonResponse
from .utils import get_stock_data

def search_stock(request):
    query = request.GET.get('query')
    if query:
        # Assuming query is the stock name, we need to pass it directly to the function
        stock_price = get_stock_data(query)
        
        if stock_price is None:
            return JsonResponse({'error': 'Stock not found'}, status=404)
        
        # Return the stock price to the frontend
        return JsonResponse({'price': stock_price})
    return JsonResponse({'error': 'No stock query provided'}, status=400)


def buy_stock(request):
    if request.method == 'POST':
        # Retrieve the data from the form submission
        stock_symbol = request.POST.get('symbol')
        quantity = int(request.POST.get('quantity'))
        price_per_share = Decimal(request.POST.get('price'))  # Price per share
        total_amount = price_per_share * quantity  # Calculate total amount

        # Get the user's wallet balance
        user = request.user
        wallet_balance = user.wallet_balance  # Assuming you have a wallet balance field in the user model

        if total_amount > wallet_balance:
            # If the user doesn't have enough balance, show an error
            messages.error(request, "Insufficient funds in your wallet.")
            return redirect('buy_stock')  # Redirect back to the buy stock page

        # Deduct the total amount from the user's wallet
        user.wallet_balance -= total_amount
        user.save()  # Save the updated user instance

        # Check if the user already owns this stock in their portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            stock_symbol=stock_symbol,
            defaults={'quantity': 0, 'average_price': price_per_share}
        )

        if not created:
            # Update the average price and quantity if the stock is already in the portfolio
            total_quantity = portfolio.quantity + quantity
            portfolio.average_price = (
                (portfolio.average_price * portfolio.quantity) + (price_per_share * quantity)
            ) / total_quantity
            portfolio.quantity = total_quantity
        else:
            # If it's a new stock, set the purchase price (average price) and quantity
            portfolio.quantity = quantity
            portfolio.average_price = price_per_share

        portfolio.save()

        # Record the stock transaction
        StockTransaction.objects.create(
            user=user,
            stock_symbol=stock_symbol,
            transaction_type='buy',
            quantity=quantity,
            price_per_share=price_per_share
        )

        # Record the wallet deduction in the user's transaction history
        Transaction.objects.create(
            user=user,
            transaction_type='buy_stock',  # Meaningful transaction type
            amount=total_amount
        )

        # Show success message and redirect
        messages.success(request, f"Successfully bought {quantity} shares of {stock_symbol}.")
        return redirect('company_shares')  # Redirect to a dashboard or any other page

    # If the request is GET, simply render the buy stock page (you can customize this view)
    return render(request, 'company_shares.html')

def get_stock_price(request):
    print("get_stock_price view called!")  # Debugging
    stock_symbol = request.GET.get('symbol')  # Retrieve the stock symbol from the request
    print(f"Received stock symbol: {stock_symbol}")  # Debugging

    if stock_symbol:
        price = get_stock_data(stock_symbol)
        print(f"Price fetched for {stock_symbol}: {price}")  # Debugging output
        if price:
            return JsonResponse({'price': price})
        else:
            print("Price not found or invalid response from API.")
    return JsonResponse({'price': None}, status=404)