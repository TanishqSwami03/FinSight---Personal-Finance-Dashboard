from django.db import models

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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="portfolio", null = True, blank = True)
    stock_symbol = models.CharField(max_length=10)
    company_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def total_value(self):
        return self.current_price * self.quantity

    @property
    def profit(self):
        return (self.current_price - self.purchase_price) * self.quantity

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
