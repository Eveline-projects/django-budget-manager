from django.http import HttpResponse
from django.shortcuts import render

from edu.froms import DayForm
from edu.models import Day


def hello(request):
    return HttpResponse("Hello, world.")


def greet(request, name):
    return HttpResponse(f"hello, {name}!")


def welcome(request):
    return render(request,"edu/welcome.html",{})


def person(request, name, age, city, hobby):
    context = {
        'name': name,
        'age': age,
        'city': city,
        'hobby': hobby,
    }
    return render(request,'edu/person.html',context)


def day_view(request):
    if request.method == 'POST':
        form = DayForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            summary = form.cleaned_data['summary']
            date = form.cleaned_data['date']
            print(title, summary, date)
            day_db = Day(title=title, summary=summary, date=date)
            day_db.save()

    else:
        form = DayForm()

    return render(request,'edu/day_view.html',{'form':form})

def day_list(request):
    days = Day.objects.all()
    return render(request,'edu/list.html',{'days':days})

