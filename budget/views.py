from django.shortcuts import render, redirect
from .forms import RegisterForm
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
    form_class = UserCreationForm
    template_name = 'budget/register.html'
    success_url = reverse_lazy('budget:expense')


    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ExpenseListView(ListView):
    template_name = 'budget/expense.html'
    context_object_name = 'expenses'
    queryset = Expense.objects.all()
    paginate_by = 10
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# class CategoryListView(ListView):
#     template_name = 'budget/category.html'
#     context_object_name = 'categories'
#     queryset = Category.objects.all()
#     paginate_by = 10

class BankAccountListView(ListView):
    template_name = 'budget/account.html'
    context_object_name = 'accounts'
    queryset = BankAccount.objects.all()
    paginate_by = 10
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_queryset(self):
      if user == self.request.user:
        return BankAccount.objects.filter(user=self.request.user)
      else:
           return print('Error')



class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'budget/login.html'
    success_url = reverse_lazy('budget:expense')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

