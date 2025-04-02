from django.contrib import admin
from .models import StockData , Transaction ,Portfolio  # Import your model
# Register your models here.

admin.site.register(StockData)
admin.site.register(Transaction)
admin.site.register(Portfolio)