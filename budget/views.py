from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import  reverse_lazy
from django.db.models import Sum, Q
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView,
    View,
    TemplateView
)

from .models import (
    Transaction,
    Category,
    BankAccount,
    SavingsAccount, Target
)
from .forms import (
    RegisterForm,
    BankAccountForm,
    BankAccountCreateForm,
    BankAccountUpdateForm,
    SavingAccountForm,
    TransactionForm
)
import json

class IndexView(TemplateView):
    template_name = 'index.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('budget:expense')
        return super().get(request, *args, **kwargs)

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'budget/register.html'
    success_url = reverse_lazy('budget:transaction')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        default_categories = [
            'Food',
            'Bills',
            'Transport',
            'Entertainment',
            'Shopping',
            'Life',
            'Investments',
            'Other',
        ]
        for name in default_categories:
            Category.objects.get_or_create(
                user=self.object,
                name=name
            )

        return response


class TransactionListView(LoginRequiredMixin, ListView):
    template_name = 'budget/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        sort_by = self.request.GET.get('sort', '-date')
        columns = [
            'amount', '-amount',
            'date', '-date',
            'category__name', '-category__name'
        ]
        if sort_by not in columns:
            sort_by = '-date'
        return Transaction.objects.filter(user=self.request.user).order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user


        user_transactions = Transaction.objects.filter(user=user)
        user_accounts = BankAccount.objects.filter(user=user)

        total_out = user_transactions.filter(type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_transactions'] = total_out


        context['total_balance'] = sum(acc.total_balance for acc in user_accounts)


        context['categories'] = Category.objects.filter(user=user)
        context['transaction_count'] = user_accounts.count()
        context['savings_count'] = SavingsAccount.objects.filter(user=user).count()


        context['total_savings'] = SavingsAccount.objects.filter(user=user).count()
        context['target'] = Target.objects.filter(user=user).count()


        stats_query = user_transactions.filter(type='OUT') \
            .values('category__name') \
            .annotate(total=Sum('amount')) \
            .order_by('-total')

        labels = [item['category__name'] for item in stats_query if item['category__name']]
        values = [float(item['total']) for item in stats_query]

        context['labels'] = json.dumps(labels)
        context['values'] = json.dumps(values)

        return context


class HomeTransactionListView(TransactionListView):
    template_name = 'budget/transaction.html'
    paginate_by = None
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')[:5]

class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount
    template_name = 'budget/account.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BankAccountCreateForm(user=self.request.user)
        return context


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountCreateForm
    template_name = 'budget/account.html'
    success_url = reverse_lazy('budget:account')

    def form_valid(self, form):
        form.instance.user = self.request.user
        amount = form.cleaned_data.get('initial_balance') or 0
        form.instance.initial_balance = 0
        account = form.save()


        if amount > 0:
            category = form.cleaned_data.get('category')
            if not category:
                category, _ = Category.objects.get_or_create(
                    name="Other",
                    user=self.request.user
                )

            Transaction.objects.create(
                user=self.request.user,
                amount=amount,
                type='IN',
                category=category,
                account=account,
                description="Starting balance"
            )
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = BankAccount.objects.filter(user=self.request.user)
        return context


class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountUpdateForm
    template_name = 'budget/account_update.html'
    success_url = reverse_lazy('budget:account')

    def get_initial(self):
        initial = super().get_initial()
        account = self.get_object()
        initial['initial_balance'] = account.total_balance
        return initial

    def form_valid(self, form):
        target_balance = form.cleaned_data['initial_balance']
        account = self.get_object()
        agg = account.transactions.aggregate(
            incomes=Sum('amount', filter=Q(type='IN')),
            outcomes=Sum('amount', filter=Q(type='OUT')),
        )
        transactions_sum = (agg['incomes'] or 0) - (agg['outcomes'] or 0)
        form.instance.initial_balance = target_balance - transactions_sum
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccount
    success_url = reverse_lazy('budget:account')

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'budget/login.html'
    success_url = reverse_lazy('budget:transaction')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budget/transaction_create.html'
    success_url = reverse_lazy('budget:transaction')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('budget:login')


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'budget/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'budget/category_create.html'
    success_url = reverse_lazy('budget:transaction')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SavingCreateView(LoginRequiredMixin, CreateView):
    model = SavingsAccount
    form_class = SavingAccountForm
    template_name = 'budget/saving_add.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['savings'] = SavingsAccount.objects.filter(user=self.request.user).order_by('-id')
        return context


class SavingDetailView(LoginRequiredMixin, DetailView):
    model = SavingsAccount
    template_name = 'budget/saving_detail.html'
    context_object_name = 'saving_detail'

    def get_queryset(self):
        return SavingsAccount.objects.filter(user=self.request.user).order_by('-id')


class SavingListView(LoginRequiredMixin, ListView):
    model = SavingsAccount
    template_name = 'budget/saving_list.html'
    context_object_name = 'savings'

    def get_queryset(self):
        return SavingsAccount.objects.filter(user=self.request.user).order_by('-id')


class TargetCreateView(LoginRequiredMixin, CreateView):
    model = Target
    fields = ['target_type', 'target_balance']
    template_name = 'budget/target.html'
    success_url = reverse_lazy('budget:target_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target'] = Target.objects.filter(user=self.request.user).order_by('-id')
        return context

class TargetListView(LoginRequiredMixin, ListView):
    model = Target
    template_name = 'budget/target_list.html'
    context_object_name = 'targets'

    def get_queryset(self):
        return Target.objects.filter(user=self.request.user).order_by('-id')

class DetailView(TransactionListView):
    template_name = 'budget/detail.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats_query = Transaction.objects.filter(user=self.request.user, type='OUT') \
            .values('category__name') \
            .annotate(total=Sum('amount')) \
            .order_by('-total')

        context['labels'] = json.dumps([item['category__name'] for item in stats_query])
        context['values'] = json.dumps([float(item['total']) for item in stats_query])
        return context

