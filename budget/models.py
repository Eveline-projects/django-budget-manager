from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.apps import AppConfig
from django.core.signals import request_finished
from django.conf import settings

# class MyAppConfig(AppConfig):
#     def ready(self):
#         from . import signals
#         request_finished.connect(signals.my_callback)
#
#     @receiver(pre_save, sender=MyModel)
#     def my_handler(sender, **kwargs):
#


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    TYPE_ACCOUNT = [
        ('ADULT', 'Adult'),
        ('CHILD', 'Child'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name_account = models.CharField(max_length=50)
    account_type = models.CharField(max_length=10, choices=TYPE_ACCOUNT, default='ADULT')
    account_creation_date = models.DateTimeField(default=timezone.now)


    @property
    def total_balance(self):
        incomes = sum(e.amount for e in self.expenses.filter(type='IN'))
        outcomes = sum(e.amount for e in self.expenses.filter(type='OUT'))
        return incomes - outcomes

    def get_balance(self):
        all_entries = self.expenses.all()

        total = 0
        for entry in all_entries:
            if entry.type == 'IN':
                total += entry.amount
            else:
                total -= entry.amount
        return total

    def __str__(self):
        return f"{self.name_account} - Balance: {self.total_balance}"




class Expense(models.Model):
    TYPE_CHOICES = [
        ('OUT', 'Expense'),
        ('IN', 'Deposit'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='OUT')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='expenses')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.type == 'IN':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.save()

    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} PLN ({self.category})"







