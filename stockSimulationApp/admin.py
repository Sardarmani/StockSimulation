from django.contrib import admin
from .models import StockData , Transaction ,Portfolio  ,Watchlist# Import your model
# Register your models here.

admin.site.register(StockData)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Watchlist)