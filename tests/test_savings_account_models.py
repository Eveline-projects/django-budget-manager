import pytest
from django.urls import reverse
from decimal import Decimal
from budget.models import SavingsAccount



def test_savings_account_should_check_correct_name(savings_account):
    assert savings_account.saving_name == 'saving account'


def test_savings_account_should_have_correct_saving_type(savings_account):
    assert savings_account.saving_type == 'DEPOSITS'


def test_savings_account_should_have_saving_balance(savings_account):
    assert savings_account.saving_balance == Decimal('10000.00')


def test_savings_account_should_delete_saving_account(savings_account):
    account_id = savings_account.id
    savings_account.delete()
    assert SavingsAccount.objects.filter(id=account_id).count() == 0


def test_savings_account_should_save_saving_account(savings_account):
    savings_account.saving_name = "NEW"
    savings_account.save()
    savings_account.refresh_from_db()
    assert savings_account.saving_name == "NEW"


def test_savings_account_should_get_absolute_url(savings_account):
    expected_url = reverse("budget:saving_detail", kwargs={"pk": savings_account.pk})
    assert savings_account.get_absolute_url() == expected_url


def test_savings_account_string_representation(savings_account, user):
    expected_str = f"{user}: saving account (DEPOSITS)"
    assert str(savings_account) == expected_str
