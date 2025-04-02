import asyncio
import base64
import pandas as pd
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
 # Your data fetching service
from ...utils.chart_generators import historical

from ...utils.data_fetchers import get_stock_data
import json

@method_decorator(csrf_exempt, name='dispatch')
class StockChartAPIView(APIView):
    """API endpoint to fetch historical stock data and generate a chart"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint

    def get(self, request, ticker, timeframe="1M"):
        try:
            print("FLuteerr")
            df = get_stock_data(ticker)
            print(df.head())
            df = df.rename(columns={
            "open_price": "open",
            "price": "close"  # Assuming 'price' is the closing price
            })
    
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")  # Convert to float
            df["volume"].fillna(0, inplace=True)  
            print(df.head())
            # 🔹 Call function from historical.py to generate the chart
            response = historical.generate_stock_plot(df)

            # 🔹 Extract base64 image from response
            # response_data = response.json()  # Convert JsonResponse to Python dict
            response_data = json.loads(response.content)  # Corrected
            if "error" in response_data:
                return Response({"status": "error", "message": response_data["error"]}, status=400)

            image_base64 = response_data.get("image", "")

            return Response({
                "status": "success",
                "image": image_base64
            })
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)
