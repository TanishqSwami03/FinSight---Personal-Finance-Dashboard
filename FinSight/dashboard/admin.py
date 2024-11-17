from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(StockTransaction)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'date')

    def delete_model(self, request, obj):
        # Adjust the user's wallet balance before deletion
        if obj.transaction_type == 'add':
            obj.user.wallet_balance -= obj.amount
        elif obj.transaction_type == 'receive':
            obj.user.wallet_balance -= obj.amount
        elif obj.transaction_type == 'send':
            obj.user.wallet_balance += obj.amount

        obj.user.save()  # Save the updated wallet balance
        super().delete_model(request, obj)  # Proceed with the deletion

admin.site.register(Transaction, TransactionAdmin)