import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from budget.models import Transaction


@pytest.mark.django_db
class TestTransactionViews:

    @pytest.fixture(autouse=True)
    def setup_view_data(self, client, user):
        client.force_login(user)

    def test_transaction_list_status_code(self, client):
        response = client.get(reverse('budget:transaction_list'))
        assert response.status_code == 200

    def test_total_expenses_calculation(self, client, user, category, bank_account):
        Transaction.objects.create(user=user, amount=100, type='OUT', category=category, account=bank_account)
        Transaction.objects.create(user=user, amount=50, type='OUT', category=category, account=bank_account)

        response = client.get(reverse('budget:transaction_list'))

        assert response.context['total_transactions'] == 150

    def test_transaction_list_privacy(self, client, user, transaction, bank_account, category):
        another_user = User.objects.create_user(username='hacker', password='testpassword123')
        secret_transaction = Transaction.objects.create(
            user=another_user,
            amount=999,
            type='OUT',
            description="Secret",
            account=bank_account,
            category=category
        )
        response = client.get(reverse('budget:transaction_list'))
        assert response.status_code == 200
        assert transaction in response.context['transactions']
        assert secret_transaction not in response.context['transactions']

    def test_bank_account_creation_tiggers_transaction(self, client, user, category):
        data = {
            'name_account': 'Wallet',
            'account_type': 'ADULT',
            'initial_balance': 500,

        }
        response = client.post(reverse('budget:account_create'), data=data, follow=True)
        assert response.status_code == 200
        assert Transaction.objects.filter(amount=500, description="Starting balance", user=user).exists()
