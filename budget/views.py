from django.http import HttpResponse
from django.shortcuts import render,redirect
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


def homepage(request):
    return HttpResponse("Homepage działa")
    # return render(request, 'budget/homepage.html')
