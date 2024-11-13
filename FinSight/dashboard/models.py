from django.db import models

from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()  # This will now refer to CustomUserModel

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('send', 'Send Money'),
        ('receive', 'Receive Money'),
        ('add', 'Add Money'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₹{self.amount} on {self.date}"