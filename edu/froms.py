from django import forms

class DayForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput())
    summary = forms.CharField(widget=forms.Textarea())
    date = forms.DateField(widget=forms.TextInput())
