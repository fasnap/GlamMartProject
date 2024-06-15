from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from . models import UserAccount

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder' : 'Enter password',
        'name': 'password'
    }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder' : 'Enter password again',
        'name': 'confirm_password'
    }))
    class Meta:
        model= UserAccount
        fields=['first_name','last_name','username','email','phone_number','password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email', 'name':'email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name', 'name':'first_name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name', 'name':'last_name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Userame', 'name':'username'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number', 'name':'phone_number'}),
        }
    
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
        
    def clean_first_name(self):
        first_name= self.cleaned_data.get('first_name').strip()
        if len(first_name) < 3:
            raise forms.ValidationError("First name must be at least 3 characters long.")
        if ' ' in first_name:
            raise forms.ValidationError("First name must not contain spaces.")
        return first_name
    
    def clean_last_name(self):
        last_name= self.cleaned_data.get('last_name').strip()
        if len(last_name) < 1:
            raise forms.ValidationError("Last name must be at least 1 characters long.")
        if ' ' in last_name:
            raise forms.ValidationError("Last name must not contain spaces.")
        return last_name

    def clean_username(self):
        username= self.cleaned_data.get('username').strip()
        if len(username) < 1:
            raise forms.ValidationError("Username must be at least 4 characters long.")
        if ' ' in username:
            raise forms.ValidationError("Username must not contain spaces.")
        return username

