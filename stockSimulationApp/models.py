from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)  # Starting balance

    def __str__(self):
        return f"{self.user.username}'s Portfolio"

class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} shares of {self.ticker} at ${self.price}"

class StockData(models.Model):
    company_ticker = models.CharField(max_length=10 ,db_index=True)
    date = models.DateField()
    price = models.FloatField()
    open_price = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    volume = models.CharField(max_length=50)  # Store as string if large numbers
    change_percent = models.FloatField()

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticker')  # Prevent duplicate entries for same user and ticker