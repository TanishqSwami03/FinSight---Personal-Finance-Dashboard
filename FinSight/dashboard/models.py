from django.db import models
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()  # This will now refer to CustomUserModel

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('send', 'Send Money'),
        ('receive', 'Receive Money'),
        ('add', 'Add Money'),
        ('buy_stock', 'Buy Stock'),
        ('sell_stock', 'Sell Stock'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₹{self.amount} on {self.date}"


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="portfolio", null=True, blank=True)
    stock_symbol = models.CharField(max_length=20)
    stock_name = models.CharField(max_length=100)
    exchange_code_nse = models.CharField(max_length=20, blank=True, null=True)  # New Field
    exchange_code_bse = models.CharField(max_length=20, blank=True, null=True)  # New Field
    quantity = models.PositiveIntegerField()
    average_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def invested_value(self):
        return self.average_price * self.quantity

    def get_current_price(self):
        from .utils import get_stock_data
        stock_data = get_stock_data(self.stock_symbol)

        if stock_data and 'current_price_nse' in stock_data:
            try:
                # Extract the stock price and convert it to Decimal
                current_price = Decimal(stock_data['current_price_nse'])
                return current_price
            except Exception as e:
                print(f"Error converting stock price to Decimal: {e}")
                return Decimal(0)  # Default to 0 if there's an error
        else:
            print("Invalid stock data received or missing 'current_price_nse'")
            return Decimal(0)
    
    @property
    def profit(self):
        current_price = self.get_current_price()
        return (current_price - self.average_price) * self.quantity

    @property
    def percentage_change(self):
        current_price = self.get_current_price()
        return ((current_price - self.average_price) / self.average_price) * 100


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=10)
    stock_name = models.CharField(max_length=255, default = 'Unknown Stock')  # Save stock name for each transaction
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)