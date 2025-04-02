# stocks/utils/data_fetchers.py
from ..models import StockData
import pandas as pd

def get_stock_data(ticker):
    """Fetch stock data for the given ticker from the database efficiently."""
    stock_entries = StockData.objects.filter(company_ticker=ticker).only("date", "open_price", "high", "low", "price", "volume").order_by("date").iterator()
    
    # Convert to DataFrame
    data = pd.DataFrame.from_records(
        (entry.__dict__ for entry in stock_entries), columns=["date", "open_price", "high", "low", "price", "volume"]
    )
    
    if data.empty:
        return None  # Return None if no data is found

    data["date"] = pd.to_datetime(data["date"])  # Convert date to datetime
    
    print("lennnnnnnnnnnnn", len(data))

    return data
