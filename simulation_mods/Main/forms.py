from django.forms import ModelForm
from .models import Modsinfo
from django import forms

class modform(ModelForm):
    class Meta:
        model = Modsinfo
        fields='__all__'
        exclude = ['user','downloads','likes']
        widgets = {
            'uploaded_on': forms.DateTimeInput(attrs={'type': 'datetime-local','class':'form-control'}), 
        }