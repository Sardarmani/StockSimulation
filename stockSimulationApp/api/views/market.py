# api/views/market.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ...utils.market_data import MarketDataService
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class CompanyDataAPIView(APIView):
    """API endpoint for company-specific data"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    
    def get(self, request, ticker):
        try:
            data = asyncio.run(MarketDataService.get_company_data(ticker))
            return Response({
                'status': 'success',
                'data': data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MarketSummaryAPIView(APIView):
    """API endpoint for market summary data"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    
    def get(self, request):
        try:
            data = asyncio.run(MarketDataService.get_market_summary())
            print("Market Data " ,data)
            return Response({
                'status': 'success',
                'data': data,
                
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
