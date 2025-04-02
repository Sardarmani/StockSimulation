### LLM #####


# stocks/utils/financial_analysis.py
import os
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class FinancialAnalyzer:
    SYSTEM_PROMPT = {
        "role": "system",
        "content": "You are a financial analyst. Analyze the uploaded financial statement and provide a summary.",
    }

    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY") 
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None

    def extract_text_from_pdf(self, pdf_file):
        """Extracts text from an uploaded PDF file."""
        pdf_text = ""
        try:
            with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
                for page in pdf:
                    pdf_text += page.get_text("text") + "\n"
            return pdf_text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text: {str(e)}")

    def analyze_statement(self, financial_data, user_question=None):
        """Generates financial analysis using Groq API."""
        if not self.client:
            raise ValueError("API key is missing or invalid")

        try:
            messages = [self.SYSTEM_PROMPT]
            
            if user_question:
                messages.append({
                    "role": "user", 
                    "content": f"{user_question}\n\nFinancial Data: {financial_data}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"Analyze this financial statement:\n\n{financial_data}"
                })

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile"
                # llama-3.3-70b-versatile
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            raise ValueError(f"Error calling LLM: {str(e)}")


# Utility functions for Django-specific operations
def handle_financial_upload(request):
    """Handles PDF upload and initial analysis."""
    from ..forms import FinancialUploadForm  # Local import to avoid circular imports
    
    if request.method != "POST":
        
        return None, FinancialUploadForm(), None

    upload_form = FinancialUploadForm(request.POST, request.FILES)
    if not upload_form.is_valid():
        print("ASAS")
        return None, upload_form, None

    analyzer = FinancialAnalyzer()
    pdf_file = upload_form.cleaned_data["pdf_file"]
    
    try:
        extracted_text = analyzer.extract_text_from_pdf(pdf_file)
        analysis_result = analyzer.analyze_statement(extracted_text)
        print(f"Extracted Text: {analysis_result}")  # Debugging
        request.session["financial_data"] = extracted_text
        return analysis_result, upload_form, None
    except ValueError as e:
        
        return str(e), upload_form, None


def handle_financial_question(request):
    """Handles user questions about uploaded financial data."""
    from ..forms import FinancialQuestionForm  # Local import to avoid circular imports
    
    if request.method != "POST":
        print("S")
        return None, FinancialQuestionForm()

    if hasattr(request, 'data'):  # JSON request
        question_form = FinancialQuestionForm(request.data)
    else:  # Form data request
        question_form = FinancialQuestionForm(request.POST)

    
    if not question_form.is_valid():
        print("SSS")
        return None, question_form

    financial_data = request.session.get("financial_data", "")
    if not financial_data:
        print("SSSS")
        return "No financial data found. Please upload a document first.", question_form

    analyzer = FinancialAnalyzer()
    user_question = question_form.cleaned_data["user_question"]
    print(user_question)
    try:
        return analyzer.analyze_statement(financial_data, user_question), question_form
    except ValueError as e:
        return str(e), question_form
