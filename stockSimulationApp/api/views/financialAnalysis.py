# api/views/financial_analysis.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser

from ...forms import FinancialUploadForm, FinancialQuestionForm
from ...utils.financial_analysis import handle_financial_upload, handle_financial_question

@method_decorator(csrf_exempt, name='dispatch')
class FinancialUploadAPIView(APIView):
    """API endpoint for financial document upload and analysis"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        try:
            analysis_result, _, _ = handle_financial_upload(request)
            return Response({
                'status': 'success',
                'data': analysis_result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FinancialQuestionAPIView(APIView):
    """API endpoint for asking financial questions"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    
    def post(self, request):
        try:
            user_question_result, _ = handle_financial_question(request)
            return Response({
                'status': 'success',
                'data': user_question_result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FinancialAnalysisStatusAPIView(APIView):
    """API endpoint to check analysis status/results"""
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this endpoint
    
    def get(self, request):
        # You might want to implement session-based retrieval
        # or use some temporary storage for mobile clients
        return Response({
            'status': 'error',
            'message': 'Not implemented yet'
        }, status=501)