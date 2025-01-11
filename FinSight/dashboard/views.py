from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.contrib import  messages
from django.db.models import Sum, F, Sum
from django.http import JsonResponse
from .models import *
import json
from .utils import *
# Create your views here.

User = get_user_model()


def dashboard(request):
    # Get the logged-in user
    user = request.user

    if user.is_authenticated:
        # Get top stocks
        # top_stocks = get_top_stocks()
        # for stock in top_stocks:
        #     stock['change_class'] = 'text-success' if stock['percent_change'] >= 0 else 'text-danger'
        #     stock['icon_class'] = 'bi-caret-up-fill' if stock['percent_change'] >= 0 else 'bi-caret-down-fill'
        #     stock['percent_change'] = abs(stock['percent_change'])

        # print(top_stocks)

        # Get the user's wallet balance
        wallet_balance = user.wallet_balance

        # Initialize portfolio summary values
        total_value = Decimal('0.0')
        total_investment = Decimal('0.0')
        total_profit = Decimal('0.0')

        # Fetch user's portfolio
        user_portfolio = Portfolio.objects.filter(user=user)

        for portfolio in user_portfolio:
            try:
                # Fetch current price
                current_price_str = portfolio.get_current_price()  # Returns as string
                current_price = Decimal(current_price_str)  # Convert to Decimal for calculation
                
                # Calculate derived values
                average_price = portfolio.average_price
                invested_value = portfolio.quantity * average_price
                profit = (current_price - average_price) * portfolio.quantity

                # Update portfolio summary
                total_value += current_price * portfolio.quantity
                total_investment += invested_value
                total_profit += profit
            except Exception as e:
                print(f"Error processing stock {portfolio.stock_symbol}: {e}")

        # Fetch the portfolio distribution for pie chart
        portfolio_data = (
            Portfolio.objects.filter(user=user)
            .annotate(total_investment=F('average_price') * F('quantity'))
            .values('stock_symbol', 'total_investment')
        )

        # Sort portfolio by total investment in descending order
        sorted_portfolio = sorted(portfolio_data, key=lambda x: x['total_investment'], reverse=True)

        # Separate the top 4 stocks and group the rest as "Others"
        top_stocks = sorted_portfolio[:4]
        other_stocks = sorted_portfolio[4:]

        # Calculate total investment for "Others" category
        others_total = sum(stock['total_investment'] for stock in other_stocks)

        # Prepare labels and values for the pie chart
        portfolio_chart_data = {
            "labels": [stock['stock_symbol'] for stock in top_stocks],
            "values": [float(stock['total_investment']) for stock in top_stocks],
        }

        # Add "Others" to the chart if there are additional stocks
        if others_total > 0:
            portfolio_chart_data["labels"].append("Others")
            portfolio_chart_data["values"].append(float(others_total))

        # Format values for rendering in the template
        def format_currency(value):
            if value >= 10000000:
                return f"₹{(value / 10000000):.2f} Cr"  # Crore
            if value >= 100000:
                return f"₹{(value / 100000):.2f} L"  # Lakh
            return f"₹{value:.2f}"

        # Format profit/loss revenue for UI
        profit_loss_revenue = total_profit
        profit_loss_class = 'text-success' if profit_loss_revenue >= 0 else 'text-danger'

        # Pass data to the template
        return render(request, 'dashboard.html', {
            'top_stocks': top_stocks,
            'wallet_balance': format_currency(wallet_balance),
            'portfolio_chart_json': json.dumps(portfolio_chart_data),  # Pass chart data
            'total_portfolio_value': format_currency(total_investment),  # Total invested amount
            'current_value': format_currency(total_value),  # Current value
            'profit_loss_revenue': format_currency(profit_loss_revenue),  # Profit/Loss revenue
            'profit_loss_class': profit_loss_class,  # CSS class for Profit/Loss
        })
    else:
        return redirect('login')

def transaction(request):
    # Fetch transactions only for the logged-in user
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')  # Sort by date descending

    return render(request, 'transaction.html', {
        'transactions': transactions,
    })

def portfolio(request):
    return render(request, 'portfolio.html')

def wallet(request):
    user = request.user

    # Get the total income and total expense for the logged-in user
    total_income = Transaction.objects.filter(user=request.user, transaction_type='receive').aggregate(total_income=Sum('amount'))['total_income'] or Decimal(0)
    total_expense = Transaction.objects.filter(user=request.user, transaction_type='send').aggregate(total_expense=Sum('amount'))['total_expense'] or Decimal(0)

    # Fetch recent transactions (including shares bought and sold)
    transactions = Transaction.objects.filter(user=user).order_by('-date')[:6]

    # Fetch stock transactions
    stock_transactions = StockTransaction.objects.filter(user=user).order_by('-transaction_date')[:6]

    # Portfolio and other calculations remain unchanged
    portfolio = Portfolio.objects.filter(user=request.user)
    total_value = 0.0
    total_investment = 0.0
    total_profit_loss = 0.0

    if portfolio.exists():
        for stock in portfolio:
            current_price = stock.get_current_price()
            if current_price is not None:
                current_value = stock.quantity * float(current_price)
                total_value += current_value
                total_investment += float(stock.invested_value)
                total_profit_loss += float(stock.profit)

        profit_loss_percentage = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
    else:
        profit_loss_percentage = 0

    return render(request, 'wallet.html', {
        'user': user,
        'transactions': transactions,
        'stock_transactions': stock_transactions,  # Pass plain queryset
        'total_value': total_value,
        'profit_loss_percentage': profit_loss_percentage,
        'total_income': total_income,
        'total_expense': total_expense,
    })

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

    # Fetch user portfolio, ordered by stock symbol (fallback sorting)
    user_portfolio = Portfolio.objects.filter(user=request.user).order_by('stock_symbol')
    portfolio_data = []

    # Initialize portfolio summary values
    total_value = Decimal('0.0')
    total_investment = Decimal('0.0')
    total_profit = Decimal('0.0')

    for portfolio in user_portfolio:
        try:
            # Fetch current price
            current_price_str = portfolio.get_current_price()  # Returns as string
            current_price = Decimal(current_price_str)  # Convert to Decimal for calculation
            
            # Calculate derived values
            average_price = portfolio.average_price
            invested_value = portfolio.quantity * average_price
            profit = (current_price - average_price) * portfolio.quantity
            percentage_change = ((current_price - average_price) / average_price) * 100

            # Update portfolio summary
            total_value += current_price * portfolio.quantity
            total_investment += invested_value
            total_profit += profit

            # Add to portfolio data
            portfolio_data.append({
                "stock_symbol": portfolio.stock_symbol,
                "current_price": current_price,
                "average_price": average_price,
                "quantity": portfolio.quantity,
                "invested_value": invested_value,
                "percentage_change": percentage_change,
                "profit": profit,
            })
        except Exception as e:
            print(f"Error processing stock {portfolio.stock_symbol}: {e}")

    # Sort stocks by percentage change (descending order)
    sorted_stocks = sorted(portfolio_data, key=lambda x: x['percentage_change'], reverse=True)

    # Split stocks into positive and negative changes
    positive_stocks = [stock for stock in sorted_stocks if stock['percentage_change'] >= 0]
    negative_stocks = [stock for stock in sorted_stocks if stock['percentage_change'] < 0]

    # Get top 2 positive and 2 negative stocks
    top_positive_stocks = positive_stocks[:2]
    top_negative_stocks = negative_stocks[:2]

    # Combine both lists to get the top 4 stocks
    sorted_stocks = top_positive_stocks + top_negative_stocks

    # Calculate portfolio growth percentage
    portfolio_growth = ((total_value - total_investment) / total_investment) * 100 if total_investment else 0

    return render(request, 'company_shares.html', {
        'top_stocks': top_stocks,
        'portfolios': portfolio_data,
        'sorted_stocks': sorted_stocks,
        'total_value': total_value,
        'total_investment': total_investment,
        'total_profit': total_profit,
        'portfolio_growth': portfolio_growth,
    })

@login_required
def search_stock(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({'error': 'No query provided.'}, status=400)

    # Fetch stock data using `get_stock_data` from utils.py
    stock_data = get_stock_data(query)
    if stock_data is None or stock_data['current_price_nse'] is None:
        return JsonResponse({'error': 'Stock not found or price data is unavailable.'}, status=404)

    return JsonResponse({
        'symbol': stock_data['symbol'],
        'company_name': stock_data['company_name'],
        'price': stock_data['current_price_nse'],
        'exchange_code_nse': stock_data['exchange_code_nse'],
        'exchange_code_bse': stock_data['exchange_code_bse'],
    })

@login_required
def buy_stock(request):
    if request.method == 'POST':
        # Get inputs from the form
        symbol = request.POST.get('symbol', '').strip()  # Ensure no leading/trailing spaces
        price = request.POST.get('price', '').strip()
        quantity = request.POST.get('quantity', '').strip()

        # Validate inputs
        if not symbol:
            messages.error(request, "Stock symbol is missing.")
            return redirect('company_shares')
        if not price or not quantity:
            messages.error(request, "Invalid price or quantity.")
            return redirect('company_shares')

        try:
            price_decimal = Decimal(price)
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0.")
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Invalid price or quantity format.")
            return redirect('company_shares')

        total_cost = price_decimal * Decimal(quantity)

        # Check wallet balance
        user = request.user
        if user.wallet_balance < total_cost:
            messages.error(request, "Insufficient wallet balance.")
            return redirect('portfolio')

        # Fetch stock data
        stock_data = get_stock_data(symbol)
        if not stock_data:
            messages.error(request, f"Could not fetch stock data for symbol '{symbol}'.")
            return redirect('company_shares')

        # Extract stock details
        stock_symbol = stock_data.get('symbol', symbol)
        stock_name = stock_data.get('company_name', 'Unknown Stock')

        # Update user's portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            stock_symbol=stock_symbol,
            defaults={
                'quantity': quantity,
                'stock_name': stock_name,
                'average_price': total_cost / Decimal(quantity),
            },
        )
        if not created:
            # Update existing portfolio entry
            portfolio.average_price = (
                (portfolio.average_price * portfolio.quantity + total_cost)
                / (portfolio.quantity + quantity)
            )
            portfolio.quantity += quantity
        portfolio.save()

        # Deduct the cost from the wallet
        user.wallet_balance -= total_cost
        user.save()

        messages.success(request, f"Successfully purchased {quantity} shares of {stock_symbol}.")
        return redirect('company_shares')

    # Handle invalid request methods
    messages.error(request, "Invalid request method.")
    return redirect('company_shares')

def get_stock_price(request):
    stock_symbol = request.GET.get('symbol')
    if stock_symbol:
        try:
            stock_data = get_stock_data(stock_symbol)
            # Ensure stock_data contains a price
            if stock_data and stock_data.get('current_price_nse'):
                price = stock_data['current_price_nse']
                return JsonResponse({'price': price})
            else:
                return JsonResponse({'error': 'Price not found for this stock'}, status=404)
        except Exception:
            return JsonResponse({'error': 'Failed to fetch stock price'}, status=500)

    return JsonResponse({'error': 'Stock symbol is required'}, status=400)

def sell_stock(request):
    if request.method == "POST":
        stock_symbol = request.POST.get('stock_symbol')
        if not stock_symbol:
            messages.error(request, "Stock symbol is missing!")
            return redirect('company_shares')

        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "Invalid quantity!")
            return redirect('company_shares')

        # Fetch stock data
        stock_data = get_stock_data(stock_symbol)
        if not stock_data:
            messages.error(request, "Could not fetch the stock data. Please try again later.")
            return redirect('company_shares')

        price_per_share = stock_data.get('current_price_nse')
        if not price_per_share:
            messages.error(request, "Could not fetch the stock price. Please try again later.")
            return redirect('company_shares')

        # Process the sale
        user = request.user
        portfolio = Portfolio.objects.filter(user=user, stock_symbol=stock_symbol).first()

        if not portfolio or portfolio.quantity < quantity:
            messages.error(request, "Insufficient shares to sell.")
            return redirect('company_shares')

        portfolio.quantity -= quantity
        if portfolio.quantity == 0:
            portfolio.delete()
        else:
            portfolio.save()

        total_earnings = quantity * Decimal(str(price_per_share))
        user.wallet_balance += total_earnings
        user.save()

        # Record transaction
        StockTransaction.objects.create(
            user=user,
            stock_symbol=stock_symbol,
            transaction_type="sell",
            quantity=quantity,
            price_per_share=Decimal(str(price_per_share)),
        )

        messages.success(request, f"Successfully sold {quantity} shares of {stock_symbol}.")
    return redirect('company_shares')

def insights(request):
    """
    Insights page view that fetches news for all stocks in the user's portfolio.
    """
    user = request.user
    portfolio_stocks = Portfolio.objects.filter(user=user)  # Your Portfolio model
    news_by_stock = {}

    for stock in portfolio_stocks:
        stock_symbol = stock.stock_symbol
        news = get_stock_news(stock_symbol)
        news_by_stock[stock_symbol] = news

    return render(request, "insights.html", {"news_by_stock": news_by_stock})