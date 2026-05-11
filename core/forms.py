from django import forms
from .models import (
    Job,
    Report
)
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title',
            'location',
            'electrician',
            'deadline',
            'status'
        ]
        widgets = {
            'deadline': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'job',
            'report_file'
        ]