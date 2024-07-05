from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class EditUser(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile', 'name', 'username', 'email']
        widgets = {
            'profile': forms.FileInput(attrs={
                'class': 'form-control',
            }),
            'name' : forms.TextInput(attrs={
                    'class': 'form-control',
                }),
            'username' : forms.TextInput(attrs={    
                    'class': 'form-control',
                }),
            'email' : forms.TextInput(attrs={
                    'class': 'form-control',
                }),
        }