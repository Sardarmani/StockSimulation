from django import forms
from django.db import models

class FinancialUploadForm(forms.Form):
    STATEMENT_CHOICES = [
        ('balance_sheet', 'Balance Sheet'),
        ('income_statement', 'Income Statement'),
        ('cash_flow', 'Cash Flow Statement'),
    ]

    statement_type = forms.ChoiceField(choices=STATEMENT_CHOICES, label="Select Financial Statement")
    pdf_file = forms.FileField(label="Upload Financial Document")

class FinancialQuestionForm(forms.Form):
    user_question = forms.CharField(widget=forms.Textarea, label="Ask a financial question", required=True)

