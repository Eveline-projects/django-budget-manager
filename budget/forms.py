from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BankAccount, Category, SavingsAccount


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
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="First deposit category",
    )

    class Meta(BankAccountUpdateForm.Meta):
        fields = BankAccountUpdateForm.Meta.fields + ['initial_balance', 'category']

class CategoryForm(forms.ModelForm):
    category_name = forms.CharField()


class SavingAccountForm(forms.ModelForm):
    class Meta:
        model = SavingsAccount
        fields = [
            'saving_name',
            'saving_type',
            'saving_balance',
            'interest_rate',
        ]
        labels = {
            'saving_name': 'Nazwa konta',
            'saving_type': 'Typ konta',
            'saving_balance': 'Saldo początkowe',
            'interest_rate': 'Oprocentowanie',
        }
        widgets = {
            'saving_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Np. Lokata PKO'
            }),
            'saving_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'saving_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
        }

    def clean_saving_balance(self):
        balance = self.cleaned_data['saving_balance']
        if balance < 0:
            raise forms.ValidationError("Saldo nie może być ujemne.")
        return balance
