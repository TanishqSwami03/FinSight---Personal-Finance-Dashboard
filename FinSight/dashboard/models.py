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
        ('buy_stock', 'Buy Stock'),  # New type for stock purchases
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='transactions', null = True, blank = True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₹{self.amount} on {self.date}"


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="portfolio", null=True, blank=True)
    stock_symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add = True)  # Track when the stock was added

    @property
    def invested_value(self):
        return self.average_price * self.quantity  # Total amount invested

    def get_current_price(self):
        from .utils import get_stock_data  # Assuming the API call function is in a utils.py file
        current_price = get_stock_data(self.stock_symbol)
        return Decimal(current_price)  # Convert to Decimal to match `average_price`

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
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
