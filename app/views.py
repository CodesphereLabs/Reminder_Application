from django.shortcuts import render , redirect
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request , 'index.html')

def login(request):
    return render(request , 'login.html')

def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        context = {
            "form" : form
        }
        return render(request , 'signup.html' , context=context)
    else:
        print(request.POST)
        form = UserCreationForm(request.POST)
        context = {
            "form" : form
        }
        if form.is_valid():
            user = form.save()
            print(user)
            if user is not None:
                return redirect('login')
        else:
            return render(request , 'signup.html' , context=context)
