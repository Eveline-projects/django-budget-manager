from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BankAccount, Category, SavingsAccount, Transaction, Target


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': 'Username (min. 5 characters)',
        }


class BankAccountForm(forms.ModelForm):
    initial_balance = forms.DecimalField(
        label="Starting balance",
        initial=0,
        required=False,
        help_text='Enter the current balance of this account.',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )

    class Meta:
        model = BankAccount
        fields = ['name_account', 'account_type', 'initial_balance', 'parent']
        help_texts = {
            'name_account': 'For example, My savings, Main account.',
            'parent': 'Select the parent wallet if this is to be a sub-account.'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        if user:
            qs = BankAccount.objects.filter(user=user, account_type='ADULT')
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            self.fields['parent'].queryset = qs
            self.fields['parent'].empty_label = "None (Main Account)"

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get('account_type')
        parent = cleaned_data.get('parent')

        if account_type == 'ADULT' and parent:
            self.add_error('parent', "An Adult account cannot be a sub-account of another wallet.")

        if parent and self.instance.pk and parent.pk == self.instance.pk:
            self.add_error('parent', "An account cannot be its own parent.")

        return cleaned_data


class BankAccountCreateForm(BankAccountForm):
    initial_balance = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Starting balance",
    )

    class Meta(BankAccountForm.Meta):
        fields = BankAccountForm.Meta.fields + ['initial_balance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_name_account(self):
        name = self.cleaned_data.get('name_account').strip()
        exists = BankAccount.objects.filter(
            user=self.user,
            name_account__iexact=name
        ).exclude(pk=self.instance.pk).exists()
        if exists:
            raise forms.ValidationError(
                f"You already have an account named '{name}'. Please choose a unique name."
            )

        return name


class BankAccountUpdateForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['name_account', 'account_type', 'parent', 'initial_balance']
        labels = {
            'initial_balance': 'Opening balance / Adjustment',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        if self.user:
            qs = BankAccount.objects.filter(user=self.user, account_type='ADULT')
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            self.fields['parent'].queryset = qs
            self.fields['parent'].empty_label = "None (Main Account)"

    def clean_name_account(self):

        name = self.cleaned_data.get('name_account').strip()
        exists = BankAccount.objects.filter(
            user=self.user,
            name_account__iexact=name
        ).exclude(pk=self.instance.pk).exists()

        if exists:
            raise forms.ValidationError(
                f"You already have an account named '{name}'. Please choose a different name."
            )
        return name

    def clean(self):

        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')

        if parent and self.instance.pk and parent.pk == self.instance.pk:
            self.add_error('parent', "An account cannot be its own parent!")

        return cleaned_data


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'date', 'category', 'account', 'description', 'target']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['account'].queryset = BankAccount.objects.filter(user=user)
            self.fields['target'].queryset = Target.objects.filter(user=user)

            self.fields['target'].required = False


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


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
            'saving_name': 'Account name',
            'saving_type': 'Account type',
            'saving_balance': 'Opening balance',
            'interest_rate': 'Interest rate',
        }
        widgets = {
            'saving_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g. PKO deposit'
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
            raise forms.ValidationError("The balance cannot be negative.")
        return balance


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ['target_type', 'target_name', 'target_balance']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.attrs.update({'class': 'form-control'})
