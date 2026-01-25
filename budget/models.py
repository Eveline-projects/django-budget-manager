from django.db import models
from django.utils import timezone
from django.db.models import Sum, Q
from django.conf import settings


class Category(models.Model):
    CATEGORIES = [
        ('FOOD', 'Food'),
        ('HOME', 'Home'),
        ('TRANSPORT', 'Transport'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('LIFE', 'Life'),
        ('SHOPPING', 'Shopping'),
        ('BILLS', 'Bills'),
        ('INVESTMENTS', 'Investments'),
        ('OTHER', 'Other'),
    ]
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name_account = models.CharField(max_length=50)
    account_type = models.CharField(
        max_length=10,
        choices=TYPE_ACCOUNT,
        default='ADULT'
    )
    account_creation_date = models.DateTimeField(default=timezone.now)

    # def get_queryset(self):
    #     return (
    #         BankAccount.objects
    #         .filter(user=self.request.user)
    #         .annotate(
    #             total_balance=Sum('transaction__amount',
    #                               filter=Q(transactions__type='IN')) -
    #                          Sum('transaction__amount',
    #                              filter=Q(transactions__type='OUT'))
    #         )
    #         .prefetch_related('transactions')
    #     )

    @property
    def total_balance(self):
        agg = self.transactions.aggregate(
            incomes=Sum('amount', filter=Q(type='IN')),
            outcomes=Sum('amount',filter=Q(type='OUT')),
        )
        incomes = agg['incomes'] or 0
        outcomes = agg['outcomes'] or 0
        return incomes - outcomes

    def get_balance(self):
        return self.total_balance

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


    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} PLN ({self.category})"


