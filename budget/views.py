from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .account.expenses import Expense, Category


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'budget/register.html', {'form': form})


def expense(request):
    # Przykładowe zapytania do bazy:
    last_expenses = Expense.objects.order_by('-date')[:5]  # 5 ostatnich
    total_expenses = sum(e.amount for e in Expense.objects.all())
    categories = Category.objects.all()  # musiałabyś dodać logikę zliczania

    context = {
        'last_expenses': last_expenses,
        'total_expenses': total_expenses,
        'balance': 1500,  # przykładowo
        'transaction_count': Expense.objects.count(),
        'categories': categories,
    }
    return render(request, 'budget/expense.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')
    else:
        return render(request, 'budget/login.html', {})

def homepage(request):
    return render(request, 'budget/homepage.html')