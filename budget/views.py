from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from budget.forms import UserForm
from budget.models import Login

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            print(username, password, email)
            login_db = Login(username=username, password=password, email=email)
            login_db.save()
            return redirect('homepage')
    else:
        form = UserForm()#user = User.objects.create_user(username='admin', password='', email='')
    return render(request, 'budget/log_user.html', {'form': form})
#
# def login(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')  # albo inny widok
#     else:
#         form = UserForm()
#
#     return render(request, 'log_user.html', {'form': form})

def homepage(request):

    return render(request, 'budget/homepage.html')

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth import authenticate, login
# from .forms import LoginForm
#
# def sign_in(request):
#     if request.method == 'GET':
#         form = LoginForm()
#         return render(request, 'users/login.html', {'form': form})
#     elif request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user:
#                 login(request, user)
#                 messages.success(request, f'Hi {username.title()}, welcome back!')
#                 return redirect('posts')
#         messages.error(request, 'Invalid username or password')
#         return render(request, 'users/login.html', {'form': form}