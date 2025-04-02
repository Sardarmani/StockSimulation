
###### Financial Analysis . py Imports #######
from django.shortcuts import render

from .utils.financial_analysis import handle_financial_question,handle_financial_upload
from .forms import FinancialUploadForm, FinancialQuestionForm
###### Financial Analysis . py Imports #######


#### Crawler Imports ####
from .utils.crawlers.psx import PSXScraper
from .utils.crawlers.scstrade import SCSTradeScraper
from .utils.market_data import MarketDataService 
#### Crawler Imports ####

from .utils.chart_generators import historical



from django.shortcuts import  redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Portfolio, Transaction , StockData
from decimal import Decimal
import yfinance as yf
import plotly.graph_objs as go
from plotly.offline import plot
import requests
from crawl4ai import AsyncWebCrawler
import re
import asyncio
import os
from django.core.files.storage import default_storage
from django.conf import settings
import fitz  # PyMuPDF for PDF extraction
from groq import Groq

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, DatetimeTickFormatter

import asyncio
import aiohttp
from bs4 import BeautifulSoup

import os
import fitz  # PyMuPDF for PDF extraction
from django.shortcuts import render

from groq import Groq
from dotenv import load_dotenv
import pandas as pd
load_dotenv()
import plotly.io as pio  # Add this line
# Initialize the Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None




# List of tickers
TICKERS = ['ENGRO', 'HBL', 'UBL', 'MCB', 'PSO']  # Example symbols




@login_required
def stock_prices_page(request):
    selected_ticker = request.GET.get('ticker', 'ENGRO')
    image_data = stock_chart_data(selected_ticker)

    
    # Get company data
    company_data = MarketDataService.sync_get_company_data(selected_ticker)

    print("Comapnay Data :")
    # Get market summary
    market_summary = MarketDataService.sync_get_market_summary()
    print("Comapnay Data : ")
    
    return render(request, 'stocks/stock_prices.html', {
        'company_data': company_data,
        'market_summary': market_summary,
        'selected_ticker': selected_ticker,
        'stocks': [{'ticker': t} for t in TICKERS],
        'chart_image' : image_data,
    })

# For your existing fetch_stock_price endpoint
async def fetch_and_display_stock_prices(request, ticker):
    try:
        data = await MarketDataService.get_company_data(ticker)
        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



# Fetch live prices for all tickers
#27/3/2025
# async def fetch_and_display_stock_prices(request , ticker):
#     stock_data = await fetch_stock_price(ticker)
#     print("stock_data",stock_data)
#     return JsonResponse({"Data": stock_data})

# Get historical data for a ticker
# def get_historical_data(ticker):
#     ticker = ticker.split(":")[0]  # Remove ":NASDAQ"
#     stock = yf.Ticker(ticker)
#     hist = stock.history(period="1y")  # Get 1 year of historical data
#     return hist

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


import plotly.graph_objects as go
from plotly.subplots import make_subplots

# def generate_stock_plot(df, title="Stock Historical Data"):
#     """
#     Generates an interactive stock chart with volume using Plotly.
    
#     Args:
#         df (pd.DataFrame): DataFrame containing stock data with columns:
#             - Date (datetime)
#             - Open
#             - High
#             - Low
#             - Close
#             - Volume
#         title (str): Title for the chart
    
#     Returns:
#         str: HTML string of the interactive plot
#     """
#     # Create subplots with shared x-axis
#     print('ssssssssssss ' ,df.columns)


#     fig = make_subplots(rows=2, cols=1, 
#                        shared_xaxes=True, 
#                        vertical_spacing=0.05,
#                        row_heights=[0.7, 0.3])
    
#     # Add candlestick chart
#     fig.add_trace(go.Candlestick(x=df['date'],
#                                 open=df['open_price'],
#                                 high=df['high'],
#                                 low=df['low'],
#                                 close=df['price'],
#                                 name='Price'),
#                  row=1, col=1)

#     # Add volume bar chart
#     fig.add_trace(go.Bar(x=df['date'], 
#                         y=df['volume'],
#                         name='volume',
#                         marker_color='rgba(100, 100, 100, 0.5)'),
#                  row=2, col=1)

#     # Update layout
#     fig.update_layout(
#         title=title,
#         height=800,
#         xaxis=dict(
#             rangeselector=dict(
#                 buttons=list([
#                     dict(count=1,
#                          label="1m",
#                          step="month",
#                          stepmode="backward"),
#                     dict(count=6,
#                          label="6m",
#                          step="month",
#                          stepmode="backward"),
#                     dict(count=1,
#                          label="YTD",
#                          step="year",
#                          stepmode="todate"),
#                     dict(count=1,
#                          label="1y",
#                          step="year",
#                          stepmode="backward"),
#                     dict(step="all")
#                 ])
#             ),
#             rangeslider=dict(
#                 visible=True
#             ),
#             type="date"
#         ),
#         yaxis_title='Price',
#         template='plotly_dark',  # Modern dark theme
#         hovermode='x unified',
#         showlegend=False
#     )

#     # Format volume subplot
#     fig.update_yaxes(title_text="Volume", row=2, col=1)
    
#     # Remove empty dates (weekends)
#     fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

#     # Convert to HTML
#     plot_html = fig.to_html(full_html=False, config={'displayModeBar': True})
    
#     return plot_html

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from django.http import JsonResponse
from datetime import timedelta
import plotly.express as px
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from django.http import JsonResponse
from datetime import timedelta
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from django.http import JsonResponse
from matplotlib.dates import DateFormatter
from datetime import timedelta
import pandas as pd
import io, base64
from django.http import JsonResponse
import mplfinance as mpf
import matplotlib.pyplot as plt


from datetime import timedelta
import pandas as pd
import io, base64
from django.http import JsonResponse
import mplfinance as mpf
import matplotlib.pyplot as plt


# def generate_stock_plot(df, timeframe="All"):
#     # Load stock data (replace with your actual data source)
    

#     # Filter data based on selected timeframe
#     end_date = df["date"].max()
#     if timeframe == "1D":
#         start_date = end_date - timedelta(days=1)
#     elif timeframe == "5D":
#         start_date = end_date - timedelta(days=5)
#     elif timeframe == "1M":
#         start_date = end_date - timedelta(days=30)
#     elif timeframe == "1Y":
#         start_date = end_date - timedelta(days=365)
#     elif timeframe == "5Y":
#         start_date = end_date - timedelta(days=5 * 365)
#     else:  # "All"
#         start_date = df["date"].min()

#     filtered_df = df[df["date"] >= start_date]

#     # Plot using Seaborn
#     plt.figure(figsize=(12, 6))
#     sns.lineplot(data=filtered_df, x="date", y="price", marker="o", color="blue")
#     plt.title(f"Stock Price - {timeframe}")
#     plt.xlabel("Date")
#     plt.ylabel("Stock Price ($)")
#     plt.xticks(rotation=45)
#     plt.grid(True)

#     # Convert plot to image
#     img = io.BytesIO()
#     plt.savefig(img, format="png")
#     img.seek(0)
#     encoded_img = base64.b64encode(img.getvalue()).decode("utf-8")
#     plt.close()

#     return JsonResponse({"image": encoded_img})


from django.http import HttpResponse

def stock_chart_data( ticker):
    # Get data for selected stock
    
    df =get_stock_data(ticker)
    print(df.head())
    df = df.rename(columns={
        "open_price": "open",
        "price": "close"  # Assuming 'price' is the closing price
    })
    
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")  # Convert to float
    df["volume"].fillna(0, inplace=True)  
    print(df.head())
    
    response = historical.generate_stock_plot(df, timeframe="1M")
    print(response.content)
    # Extract the image from JsonResponse
    image_base64 = response.content.decode("utf-8")  # Convert response to string
    image_data = eval(image_base64).get("image", "")  # Extract base64 string
    print("sss"  ,image_data)
    
    return image_data
    


import plotly.graph_objects as go

def plot_candlestick(data):
    """Generate an interactive candlestick chart using Plotly."""
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data["date"],
                open=data["open_price"],
                high=data["high"],
                low=data["low"],
                close=data["price"],  # Close price is stored as 'price'
                name="Stock Price"
            )
        ]
    )
    
    # Customize layout
    fig.update_layout(
        title="Stock Price Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,  # Hide range slider
        template="plotly_dark"
    )
    
    return fig


# Generate candlestick chart
def generate_chart(ticker):
    hist_data = get_historical_data(ticker)

    if hist_data.empty:
        return None

    trace = go.Candlestick(
        x=hist_data.index,
        open=hist_data['Open'],
        high=hist_data['High'],
        low=hist_data['Low'],
        close=hist_data['Close'],
        name=f"Price for {ticker}"
    )

    layout = go.Layout(
        title=f"Stock Price for {ticker}",
        xaxis={'rangeslider': {'visible': False}},
        yaxis={'title': 'Price (in $)'}
    )

    fig = go.Figure(data=[trace], layout=layout)
    return plot(fig, output_type='div')
import plotly.offline as pyo

def stock_chart(request , ticker):
    """Django view to return a JSON response with the candlestick chart."""
    data = get_stock_data(ticker)
    
    if data is None:
        return JsonResponse({"error": "No data found for this ticker"}, status=404)
    
    fig = plot_candlestick(data)
    graph_json = pio.to_json(fig)  # Convert Plotly figure to JSON
    return pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return JsonResponse({"chart": graph_json})

# # Stock prices page
# def stock_prices_page(request):
#     ticker = "ENGRO" # request.GET.get('ticker', 'AAPL:NASDAQ')  # Default ticker
#     chart = generate_chart(ticker)
#     return render(request, 'stocks/stock_prices.html', {'chart': chart, 'selected_ticker': ticker})

#27/3/2025
# import json
# @login_required(login_url='login')
# def stock_prices_page(request):
#     selected_ticker = request.GET.get('ticker', 'ENGRO')  # Get selected ticker
#     # chart = generate_chart(selected_ticker)
#     data = get_stock_data(selected_ticker)
#     print("Coumnssss " , data.columns)
#     # chart_data = generate_stock_plot(data)
#     stocks = [{'ticker': t} for t in TICKERS]
    
#     return render(request, 'stocks/stock_prices.html', {
#         'chart': None ,#chart_data,
#         'selected_ticker': selected_ticker,
#         'stocks': stocks  # Pass symbols to template
#     })

# Buy stock
@login_required
def buy_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        quantity = int(request.POST.get('quantity'))
        price = Decimal(request.POST.get('price'))

        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        total_cost = price * quantity

        if portfolio.balance >= total_cost:
            portfolio.balance -= total_cost
            portfolio.save()

            Transaction.objects.create(
                portfolio=portfolio,
                ticker=ticker,
                quantity=quantity,
                price=price,
                transaction_type='BUY'
            )
            return redirect('portfolio')
        else:
            return JsonResponse({"error": "Insufficient balance"}, status=400)

    return redirect('stock_prices_page')

# Sell stock
@login_required
def sell_stock(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        quantity = int(request.POST.get('quantity'))
        price = Decimal(request.POST.get('price'))

        portfolio = Portfolio.objects.get(user=request.user)
        total_value = price * quantity

        # Check if the user has enough shares to sell
        transactions = Transaction.objects.filter(portfolio=portfolio, ticker=ticker)
        total_shares = sum(t.quantity for t in transactions if t.transaction_type == 'BUY') - sum(t.quantity for t in transactions if t.transaction_type == 'SELL')

        if total_shares >= quantity:
            portfolio.balance += total_value
            portfolio.save()

            Transaction.objects.create(
                portfolio=portfolio,
                ticker=ticker,
                quantity=quantity,
                price=price,
                transaction_type='SELL'
            )
            return redirect('portfolio')
        else:
            return JsonResponse({"error": "Insufficient shares"}, status=400)

    return redirect('stock_prices_page')

# Portfolio page
@login_required
def portfolio(request):
    portfolio = Portfolio.objects.get(user=request.user)
    transactions = Transaction.objects.filter(portfolio=portfolio).order_by('-timestamp')
    holdings = {}

    for transaction in transactions:
        if transaction.ticker not in holdings:
            holdings[transaction.ticker] = 0
        if transaction.transaction_type == 'BUY':
            holdings[transaction.ticker] += transaction.quantity
        elif transaction.transaction_type == 'SELL':
            holdings[transaction.ticker] -= transaction.quantity

    return render(request, 'stocks/portfolio.html', {
        'portfolio': portfolio,
        'transactions': transactions,
        'holdings': holdings
    })

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('stock_prices_page')
        else:
            return render(request, 'stocks/login.html', {'error': 'Invalid credentials'})
    return render(request, 'stocks/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.models import User
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('stock_prices_page')

    return render(request, 'stocks/signup.html')

def financial_analysis_view(request):
    user_question_result = None  # Initialize the variable

    if request.method == "POST":
        if "upload_file" in request.POST:
            analysis_result, upload_form, _ = handle_financial_upload(request)
            question_form = FinancialQuestionForm()
        elif "ask_question" in request.POST:
            user_question_result, question_form = handle_financial_question(request)
            upload_form = FinancialUploadForm()
            analysis_result = None
    else:
        upload_form = FinancialUploadForm()
        question_form = FinancialQuestionForm()
        analysis_result = None
        user_question_result = None

    return render(request, "stocks/financial_analysis.html", {
        "upload_form": upload_form,
        "question_form": question_form,
        "analysis_result": analysis_result,
        "user_question_result": user_question_result,
    })

#######################   MOBIEL APP FUNCTIONALITY ##############################

from rest_framework import viewsets
from .models import Portfolio, Transaction, StockData
from .serializers import PortfolioSerializer, TransactionSerializer, StockDataSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import LoginSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class StockDataViewSet(viewsets.ModelViewSet):
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer



# @method_decorator(csrf_exempt, name='dispatch')
# class LoginAPIView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data["username"]
#             password = serializer.validated_data["password"]
#             user = authenticate(username=username, password=password)

#             if user:
#                 token, created = Token.objects.get_or_create(user=user)
#                 return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "user_id": user.pk,
                    "username": user.username,
                    "message": "Login successful"
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)