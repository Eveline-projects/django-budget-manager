import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from budget.models import SavingsAccount


@pytest.mark.django_db
class TestSavingViews:

    @pytest.fixture(autouse=True)
    def setup(self, client, user):
        client.force_login(user)

    def test_saving_list_view_displays_only_user_savings(self, client, savings_account):
        other_user = User.objects.create_user(username='hacker', password='testpassword123')
        other_saving = SavingsAccount.objects.create(
            user=other_user, saving_name="Secret", saving_balance=100
        )

        response = client.get(reverse('budget:saving_list'))

        assert response.status_code == 200
        assert savings_account in response.context['savings']
        assert other_saving not in response.context['savings']

    def test_saving_list_order_by_id_descending(self, client, user):
        s1 = SavingsAccount.objects.create(user=user, saving_name="First", saving_balance=10)
        s2 = SavingsAccount.objects.create(user=user, saving_name="Second", saving_balance=20)

        response = client.get(reverse('budget:saving_list'))
        savings = list(response.context['savings'])

        assert savings[0] == s2
        assert savings[1] == s1

    def test_saving_create_view_successful_post(self, client, user):
        url = reverse('budget:saving_add')
        data = {
            'saving_name': 'New Goal',
            'saving_type': 'DEPOSITS',
            'saving_balance': 5000.00,
            'interest_rate': 0.04
        }

        response = client.post(url, data)
        assert response.status_code == 302
        assert SavingsAccount.objects.filter(saving_name='New Goal', user=user).exists()

    def test_saving_create_view_invalid_data(self, client):
        url = reverse('budget:saving_add')
        response = client.post(url, {})

        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_saving_detail_view(self, client, savings_account):
        url = reverse('budget:saving_detail', kwargs={'pk': savings_account.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['saving_detail'] == savings_account

    def test_user_cannot_view_others_saving_detail(self, client):
        other_user = User.objects.create_user(username='other_person', password='password123')
        other_saving = SavingsAccount.objects.create(
            user=other_user, saving_name="Secret", saving_balance=500
        )

        url = reverse('budget:saving_detail', kwargs={'pk': other_saving.pk})
        response = client.get(url)

        assert response.status_code == 404
