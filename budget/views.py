from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm, BankAccountForm, BankAccountCreateForm, BankAccountUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Expense, Category, BankAccount
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    FormView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'budget/register.html'
    success_url = reverse_lazy('budget:expense')


    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ExpenseListView(LoginRequiredMixin, ListView):
    template_name = 'budget/expense.html'
    context_object_name = 'expenses'
    queryset = Expense.objects.all()
    paginate_by = 10


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Expense.objects.filter(account__user=self.request.user)


class BankAccountListView(LoginRequiredMixin, ListView):
    model = BankAccount

    template_name = 'budget/expense.html'
    context_object_name = 'accounts'
    queryset = BankAccount.objects.all()
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class BankAccountCreateView(LoginRequiredMixin, CreateView):
    model = BankAccount
    form_class = BankAccountCreateForm
    template_name = 'budget/account.html'
    success_url = reverse_lazy('budget:account')

    def form_valid(self, form):
        form.instance.user = self.request.user
        account = form.save()
        amount = form.cleaned_data.get('initial_balance')
        category = form.cleaned_data.get('category')

        if amount and amount > 0: #and category:
            Expense.objects.create(
                user=self.request.user,
                amount=amount,
                type='IN',
                # category=category,
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccount
    success_url = reverse_lazy('budget:account')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')


class CategoryListView(ListView):
    template_name = 'budget/expense.html'
    context_object_name = 'categories'
    queryset = Expense.get_category_display
    paginate_by = 10


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'budget/login.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['amount', 'category', 'description']
    template_name = 'budget/expense_create.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('budget:expense')

class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'budget/expense_detail.html'
    context_object_name = 'expense'

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).order_by('-date')
