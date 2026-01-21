from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BankAccount, Category

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BankAccountForm(forms.ModelForm):
    initial_balance = forms.DecimalField(
        label="Starting balance",
        initial=0,
        min_value=0,
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="First deposit category",
        required=False
    )
    class Meta:
        model = BankAccount
        fields = ('name_account', 'account_type')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)


class BankAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['name_account', 'account_type']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class BankAccountCreateForm(BankAccountUpdateForm):
    initial_balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
         label="Starting balance",
    )
    # category = forms.ModelChoiceField(
    #     queryset=Category.objects.all(),
    #     required=False,
    #     label="First deposit category",
    # )

    class Meta(BankAccountUpdateForm.Meta):
        fields = BankAccountUpdateForm.Meta.fields + ['initial_balance'] #'category']

