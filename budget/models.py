from django.db import models
from django.utils import timezone
from django.apps import AppConfig
from django.core.signals import request_finished
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'user')

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
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_balance(self):
        incomes = sum(e.amount for e in self.transactions.filter(type='IN'))
        outcomes = sum(e.amount for e in self.transactions.filter(type='OUT'))
        return incomes - outcomes

    def get_balance(self):
        all_entries = self.transactions.all()

        total = 0
        for entry in all_entries:
            if entry.type == 'IN':
                total += entry.amount
            else:
                total -= entry.amount
        return total

    def __str__(self):
        return f"{self.name_account} - Balance: {self.total_balance}"




class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('OUT', 'Outcome'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='OUT')
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.type == 'IN':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.save()

    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} PLN ({self.category})"


