import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from budget.models import Transaction


def test_transaction_should_have_correct_amount(transaction):
    assert transaction.amount == Decimal('50.00')


def test_transaction_should_store_correct_type(transaction):
    assert transaction.type == 'OUT'

def test_transaction_should_be_links_correctly_to_user_and_account(transaction, user, bank_account):
    assert transaction.user == user
    assert transaction.account == bank_account

def test_transaction_should_be_min_value_validator(bank_account, category, user):
    invalid_transaction = Transaction(
        amount=Decimal('-1.00'),
        type='IN',
        account=bank_account,
        category=category,
        user=user,
    )
    with pytest.raises(ValidationError):
        invalid_transaction.full_clean()

def test_transaction_amount_should_be_a_valid_number(transaction):
    assert isinstance(transaction.amount, Decimal)

def test_transaction_string_method(transaction):
    expected_str = f"Outcome: {transaction.amount} PLN (Food)"
    assert str(transaction) == expected_str

def test_transaction_should_deletion_removes_from_db(transaction):
    transaction_id = transaction.id
    transaction.delete()
    assert Transaction.objects.filter(id=transaction_id).count() == 0

def test_transaction_should_save_transaction(transaction):
    transaction.description = "New transaction"
    transaction.save()
    transaction.refresh_from_db()
    assert transaction.description == "New transaction"

def test_transaction_invalid_type_should_fail(transaction):
    transaction.type = 'XYZ'
    with pytest.raises(ValidationError):
        transaction.full_clean()



