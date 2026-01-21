from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Category(models.TextChoices):
    FOOD = "FD", _("Food")
    HOME = 'HM', _("Home")
    TRANSPORT = 'TP', _("Transport")
    ENTERTAINMENT = 'ET', _("Entertainment")
    LIFE = 'LI', _("Life")
    SHOPPING = 'SH', _("Shopping")
    BILLS = 'BL', _("Bills")
    INVESTMENTS = 'IM', _("Investments")
    OTHER = 'OT', _("Other")


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
    )

    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.OTHER,
    )

    def __str__(self):
        return f"{self.amount} PLN - {self.get_category_display()}"