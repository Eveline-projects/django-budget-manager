from django.http import HttpResponse
from django.shortcuts import render,redirect
from budget.forms import UserForm
from budget.models import Login
from .forms  import LoginForm

def register(request):
    if request.method == 'POST':    #Sprawdzenie czy jest POST - czyli czy użytkownik wysłał dane logowania z formularza. Jeśli nie zwracany jest else i wyświetla formularz.
        form = UserForm(request.POST)   #Tworzenie instancji UserForm i wypełnia danymi użytkownika (request.POST to słownik z danymi username/password/email - dzięki temu formularz można zweryfikować i przetworzyć.

        if form.is_valid():     #spr czy dane sa dobrze wypełnione.
            username = form.cleaned_data['username'] # cleanded_data to sprawdzenie danych
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            print(username, password, email)

            # Tworzenie nowego uzytkownika w bazie
            login_db = Login(username=username, password=password, email=email)
            login_db.save()
            return redirect('login')
    else:
        form = UserForm()#user = User.objects.create_user(username='admin', password='', email='')
    return render(request, 'budget/log_user.html', {'form': form})

def log_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
        try:    #pobieranie uzytkownika z bazy danych login/haslo
            login_user = Login.objects.get(username=username, password=password)
            # Zapis danych z sesji - zapamietuje że użytkownik jest zalogowany
            request.session['username'] = login_user.username
            request.session['id'] = login_user.id
            return redirect('homepage')
        except:
            return render(request, 'budget/log_in.html', {'form': UserForm}) # renderuje templatkę ponownie i użytkownik ponownie widzi formularz.
    else:
        form = LoginForm()  # user = User.objects.create_user(username='admin', password='', email='')
    return render(request, 'budget/log_in.html', {'form': form})

def homepage(request):
    return HttpResponse("Homepage działa")
    # return render(request, 'budget/homepage.html')
