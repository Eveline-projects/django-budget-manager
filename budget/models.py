from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.apps import AppConfig
from django.core.signals import request_finished

class MyAppConfig(AppConfig):
    def ready(self):
        from . import signals
        request_finished.connect(signals.my_callback)

    @receiver(pre_save, sender=MyModel)
    def my_handler(sender, **kwargs):

class Category(models.Model):
    name = models.CharField(max_length=50)


    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    account_id = models.IntegerField()

    def __str__(self):
        return f"{self.amount} PLN - {self.get_category_display()}"


class BankAccount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)




class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    account_id = models.IntegerField()
    def __str__(self):
        return f"{self.amount} PLN - {self.get_category_display()}"
