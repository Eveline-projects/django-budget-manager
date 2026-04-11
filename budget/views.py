from django.shortcuts import redirect, render
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.db.models import Sum, Q, Avg
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
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
from django.contrib.auth import get_user_model
import json
from .tokens import acc_activation_token
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

User = get_user_model()

class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('budget:transaction')
        return super().get(request, *args, **kwargs)


class RegistrationPendingView(TemplateView):
    template_name = 'budget/registration_pending.html'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'budget/register.html'
    success_url = reverse_lazy('budget:registration_pending')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

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
                user=user,
                name=name
            )
        current_site = get_current_site(self.request)
        subject = 'Activate your budget account'
        message = render_to_string('budget/acc_activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': acc_activation_token.make_token(user),
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        return redirect(self.success_url)


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and acc_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('budget:login')
        else:
            return render(request, 'budget/activation_invalid.html')


class TransactionListView(LoginRequiredMixin, ListView):
    template_name = 'budget/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        # Pobieramy bazowy queryset dla danego użytkownika
        queryset = Transaction.objects.filter(user=self.request.user)

        # 1. Filtrowanie po czasie (np. przycisk "Last 30 days")
        days = self.request.GET.get('days')
        if days and days.isdigit():
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(date__gte=start_date)

        # 2. Filtrowanie po konkretnym koncie (dla przycisku "History" z widoku kont)
        account_id = self.request.GET.get('account')
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        # 3. Obsługa sortowania
        sort_by = self.request.GET.get('sort', '-date')
        allowed_columns = [
            'amount', '-amount',
            'date', '-date',
            'category__name', '-category__name'
        ]

        if sort_by not in allowed_columns:
            sort_by = '-date'

        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_transactions = Transaction.objects.filter(user=user)
        user_accounts = BankAccount.objects.filter(user=user)

        total_out = user_transactions.filter(type='OUT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        context['total_transactions'] = total_out

        remaining_balance = sum((acc.total_balance for acc in user_accounts), Decimal('0.00'))
        context['total_balance'] = remaining_balance

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
        amount = form.cleaned_data.get('initial_balance') or 0
        category = form.cleaned_data.get('category')

        try:
            with transaction.atomic():
                form.instance.user = self.request.user
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
        except Exception as e:
            form.add_error(None, f"Critical error during account creation: {e}")
            return self.form_invalid(form)

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

        starting_transaction = Transaction.objects.filter(
            account=account,
            description='Starting balance'
        ).first()

        initial['initial_balance'] = starting_transaction.amount if starting_transaction else 0
        return initial

    def form_valid(self, form):
        account = self.get_object()
        new_target_balance = form.cleaned_data.get('initial_balance') or 0

        try:
            with transaction.atomic():
                starting_transaction = Transaction.objects.filter(
                    account=account,
                    description='Starting balance'
                ).first()
                other_transactions = account.transactions.exclude(
                    id=starting_transaction.id if starting_transaction else None
                )
                agg = other_transactions.aggregate(
                    incomes=Sum('amount', filter=Q(type='IN')),
                    outcomes=Sum('amount', filter=Q(type='OUT')),
                )
                other_sum = (agg['incomes'] or 0) - (agg['outcomes'] or 0)
                if starting_transaction:
                    starting_transaction.amount = new_target_balance - other_sum
                    starting_transaction.save()
                else:
                    Transaction.objects.create(
                        user=self.request.user,
                        amount=new_target_balance - other_sum,
                        type='IN',
                        account=account,
                        description='Starting balance',
                        category=Category.objects.get_or_create(name="Other", user=self.request.user)[0]
                    )

                form.instance.initial_balance = 0
                return super().form_valid(form)

        except Exception as e:
            form.add_error(None, f"Błąd podczas aktualizacji salda: {e}")
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccount
    success_url = reverse_lazy('budget:account')

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['targets'] = Target.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        target_id = self.request.POST.get('target')
        if target_id:
            try:
                form.instance.target_id = target_id
            except Exception as e:
                print(f"Błąd przypisania celu: {e}")
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
    success_url = reverse_lazy('budget:saving_list')

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

class SavingDeleteView(LoginRequiredMixin, DeleteView):
    model = SavingsAccount
    success_url = reverse_lazy('budget:saving_list')  

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


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


class DetailView(LoginRequiredMixin, TemplateView):
    template_name = 'budget/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user


        all_expenses = Transaction.objects.filter(user=user, type__icontains='OUT')
        print(f"Wszystkie: {Transaction.objects.filter(user=user).count()}")
        print(f"Tylko OUT: {Transaction.objects.filter(user=user, type__iexact='OUT').count()}")
        stats = all_expenses.aggregate(avg_val=Avg('amount'))
        avg = stats['avg_val'] or 0
        context['avg_expense'] = f"{float(avg):.2f}"

        # Top 3 expenses
        context['top_expenses'] = all_expenses.order_by('-amount')[:3]

        # Category counter
        context['categories'] = Category.objects.filter(user=user)

        # Chart - grouped by category
        stats_query = all_expenses.values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')

        # Preparing lists for JSON
        labels = []
        values = []
        for item in stats_query:
            if item['category__name']:
                labels.append(item['category__name'])
                values.append(float(item['total']))

        context['pie_labels'] = json.dumps(labels)
        context['pie_values'] = json.dumps(values)

        return context

class TargetDeleteView(LoginRequiredMixin, DeleteView):
    model = Target
    success_url = reverse_lazy('budget:target_list')

    def get_queryset(self):

        return Target.objects.filter(user=self.request.user)

#pdf

class GeneratePDFView(View):
    def get(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        # dane z bazy
        transactions = Transaction.objects.all()
        data = [["Data","Kategoria", "Opis", "Kwota"]]
        for t in transactions:
            data.append([
                str(t.date.strftime("%Y-%m-%d %H:%M")),
                str(t.category),
                t.description,
                str(t.amount)
            ])
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.skyblue),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        doc.build([table])
        buffer.seek(0)
        return HttpResponse(
            buffer,
            content_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=transactions.pdf"
            }
        )