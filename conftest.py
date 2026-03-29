import pytest
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User
from budget.models import BankAccount, Category, Transaction, SavingsAccount, Target

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="Test123",
        email="test123@gmail.com",
        password="testpassword123"
    )

@pytest.fixture
def category(db, user):
    return Category.objects.create(
        user=user,
        name='Food',
    )


@pytest.fixture
def bank_account(db, user):
    return BankAccount.objects.create(
        user=user,
        name_account='account1',
        initial_balance=Decimal(10000.00),
    )

@pytest.fixture
def transaction(db, user, bank_account, category):
    return Transaction.objects.create(
        amount=Decimal('50.00'),
        type='OUT',
        date=timezone.now(),
        description='Lunch',
        account=bank_account,
        category=category,
        user=user,
        )

@pytest.fixture
def savings_account(db, user):
    return SavingsAccount.objects.create(
        user=user,
        saving_name='saving account',
        saving_type='DEPOSITS',
        saving_balance=Decimal('10000.00'),
        interest_rate=0.05
    )

@pytest.fixture
def target(db):
    return Target.objects.create(
    )
