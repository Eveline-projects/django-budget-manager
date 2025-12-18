from django import forms
from .models import Login

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Login
        fields = ['username', 'password', 'email']