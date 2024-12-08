# Generated by Django 5.1.2 on 2024-12-05 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_remove_portfolio_date_added_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('send', 'Send Money'), ('receive', 'Receive Money'), ('add', 'Add Money'), ('buy_stock', 'Buy Stock'), ('sell_stock', 'Sell Stock')], max_length=10),
        ),
    ]
