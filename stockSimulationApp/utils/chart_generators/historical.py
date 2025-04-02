import io
import base64
import pandas as pd
import mplfinance as mpf
from datetime import timedelta
from django.http import JsonResponse
import  matplotlib.pyplot as  plt


plt.switch_backend("Agg")
    
def generate_stock_plot(df, timeframe="All"):
    """
    Generate a candlestick chart from stock data and return as base64 encoded image
    Args:
        df (pd.DataFrame): DataFrame containing stock data with columns:
            - date (datetime)
            - open (float)
            - high (float)
            - low (float)
            - close/price (float)
            - volume (float, optional)
        timeframe (str): Timeframe for the chart ('1D', '5D', '1M', '1Y', '5Y', 'All')
    Returns:
        JsonResponse: Contains either the base64 encoded image or error message
    """
    # Check if required columns exist
    required_cols = {"date", "open", "high", "low", "close"}
    if df.empty or not required_cols.issubset(df.columns):
        return JsonResponse({"error": "Dataframe must contain 'date', 'open', 'high', 'low', and 'close' columns"})
    
    # Convert date to datetime and set as index
    try:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        df.set_index("date", inplace=True)
    except Exception as e:
        return JsonResponse({"error": f"Date conversion error: {e}"})
    
    # Filter data based on timeframe
    end_date = df.index.max()
    if timeframe != "All":
        timeframe_dict = {
            "1D": timedelta(days=1),
            "5D": timedelta(days=5),
            "1M": timedelta(days=30),
            "1Y": timedelta(days=365),
            "5Y": timedelta(days=5 * 365)
        }
        if timeframe not in timeframe_dict:
            return JsonResponse({"error": "Invalid timeframe"})
        start_date = end_date - timeframe_dict[timeframe]
        df = df[df.index >= start_date]
    
    if df.empty:
        return JsonResponse({"error": "No data available for selected timeframe"})
    
    # Generate the plot
    fig, axlist = mpf.plot(
        df, 
        type="candle", 
        style="yahoo", 
        title=f"Stock Price History - {timeframe}",
        returnfig=True, 
        figsize=(14, 7),
        volume=True if 'volume' in df.columns else False
    )
    
    # Save to buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)  # Free memory
    
    return JsonResponse({"image": encoded_img})