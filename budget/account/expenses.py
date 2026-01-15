from django.db import models
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Zmieniamy CharField na ForeignKey (powiązanie z modelem Category)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    # account_id - jeśli masz model konta, to będzie ForeignKey.
    # Na razie zróbmy proste pole Integer:
    account_id = models.IntegerField()

    def __str__(self):
        return f"{self.amount} PLN - {self.get_category_display()}"