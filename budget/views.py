from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Expense, Category
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    FormView,
    View
)


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
