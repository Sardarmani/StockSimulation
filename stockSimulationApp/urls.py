from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortfolioViewSet, TransactionViewSet, StockDataViewSet

from .api.views.market import CompanyDataAPIView, MarketSummaryAPIView
from .api.views.getHistoricalImage import StockChartAPIView 
from .api.views.financialAnalysis import *
router = DefaultRouter()
router.register(r'api/portfolio', PortfolioViewSet)
router.register(r'api/transactions', TransactionViewSet)
router.register(r'api/stocks', StockDataViewSet)



urlpatterns = [
    
    path('', views.stock_prices_page, name='stock_prices_page'),
    path('stocks/<str:ticker>/', views.fetch_and_display_stock_prices, name='fetch_stock_prices'),
    path('stocks/<str:ticker>/chart/', views.stock_chart_data, name='stock_chart_data'),
    path('buy/', views.buy_stock, name='buy_stock'),
    path("financial-analysis/", views.financial_analysis_view, name="financial_analysis"),
    path('sell/', views.sell_stock, name='sell_stock'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/portfolio' ,PortfolioViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/', include(router.urls)),  # API endpoints are now prefixed with "api/"
    
    path('api/company/<str:ticker>/', CompanyDataAPIView.as_view(), name='company-data'),
    path('api/market-summary/', MarketSummaryAPIView.as_view(), name='market-summary'),
    path('api/stock-chart/<str:ticker>/', StockChartAPIView.as_view(), name='stock-chart'),
    path('api/financial-analysis/upload/', FinancialUploadAPIView.as_view(), name='financial_analysis_upload'),
    path('api/financial-analysis/question/', FinancialQuestionAPIView.as_view(), name='financial_analysis_question'),
    path('api/financial-analysis/status/', FinancialAnalysisStatusAPIView.as_view(), name='financial_analysis_status'),
]

