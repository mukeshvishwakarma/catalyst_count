from django import forms
from .models import DataFile

class DataFileForm(forms.ModelForm):
    class Meta:
        model = DataFile
        fields = ['file']

class FilterForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)
    locality = forms.CharField(max_length=255, required=False)
    industry = forms.CharField(max_length=255, required=False)
