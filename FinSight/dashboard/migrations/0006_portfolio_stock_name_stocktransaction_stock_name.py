# Generated by Django 5.1.2 on 2024-12-02 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_alter_portfolio_date_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='stock_name',
            field=models.CharField(default='Unknown Stock', max_length=255),
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='stock_name',
            field=models.CharField(default='Unknown Stock', max_length=255),
        ),
    ]
