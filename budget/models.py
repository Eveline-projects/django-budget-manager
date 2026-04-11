from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Q
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


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
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Account'
    )
    account_creation_date = models.DateTimeField(
        default=timezone.now
    )
    initial_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ('user', 'name_account')

    @property
    def total_balance(self):
        agg = self.transactions.aggregate(
            incomes=Sum('amount', filter=Q(type='IN')),
            outcomes=Sum('amount', filter=Q(type='OUT')),
        )

        incomes = agg['incomes'] or Decimal('0.00')
        outcomes = agg['outcomes'] or Decimal('0.00')

        return incomes - outcomes

    def __str__(self):
        return f"{self.name_account} - Balance: {self.total_balance}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Income'),
        ('OUT', 'Outcome'),
    ]
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message='The amount must be greater than zero.')]
    )
    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        default='OUT'
    )
    date = models.DateTimeField(
        default=timezone.now
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        'Target',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )

    def clean(self):
        super().clean()
        if self.type == 'OUT' and not self.category:
            raise ValidationError({
                'category': 'Category is mandatory for outcomes (expenses).'
            })

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        category_name = self.category.name if self.category else 'No Category'
        return f"{self.get_type_display()}: {self.amount} PLN ({category_name})"


class SavingsAccount(models.Model):
    TYPE_SAVE = [
        ('DEPOSITS', 'DEPOSITS'),
        ('FUNDS', 'FUNDS'),
        ('RETIREMENT', 'RETIREMENT'),
        ('OTHER', 'OTHER'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saving_name = models.CharField(max_length=50)
    saving_type = models.CharField(max_length=10, choices=TYPE_SAVE, default='DEPOSITS')
    saving_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_rate = models.FloatField(default=0.01, validators=[MinValueValidator(0)])

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user}: {self.saving_name} ({self.saving_type})"

    def get_absolute_url(self):
        if not self.pk:
            raise ValueError("Cannot reverse saving_detail because object has no PK yet")
        return reverse("budget:saving_detail", kwargs={"pk": self.pk})


class Target(models.Model):
    TYPE_CREATE = [
        ('CAR', 'CAR'),
        ('APARTMENT', 'APARTMENT'),
        ('TRAVEL', 'TRAVEL'),
        ('ENTERTAINMENT', 'ENTERTAINMENT'),
        ('EDUCATION', 'EDUCATION'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=50, choices=TYPE_CREATE, default='')
    target_name = models.CharField(max_length=100, blank=True, null=True)
    target_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def progress_percentage(self):
        from django.db.models import Sum
        # Sumujemy tylko te transakcje, które są przypisane bezpośrednio do tego celu
        total_collected = self.transactions.filter(type='IN').aggregate(Sum('amount'))['amount__sum'] or 0

        target_val = self.target_balance or 0
        if target_val > 0:
            return min(int((total_collected / target_val) * 100), 100)
        return 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user}: {self.target_type} ({self.progress_percentage}%)"
