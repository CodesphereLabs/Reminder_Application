from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginUser, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.forms import TODOForm  # Correct import
from app.models import TODO

@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user).order_by('priority')
        return render(request, 'index.html', context={'form': form, 'todos': todos})

def login(request):
    if request.method == 'GET':
        form1 = AuthenticationForm()
        context = {
            "form": form1
        }
        return render(request, 'login.html', context=context)
    else:
        form = AuthenticationForm(data=request.POST)
        print(form.is_valid())
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                loginUser(request, user)
                return redirect('home')
        else:
            context = {
                "form": form
            }
            return render(request, 'login.html', context=context)

def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        context = {
            "form": form
        }
        return render(request, 'signup.html', context=context)
    else:
        print(request.POST)
        form = UserCreationForm(request.POST)
        context = {
            "form": form
        }
        if form.is_valid():
            user = form.save()
            print(user)
            if user is not None:
                return redirect('login')
        else:
            return render(request, 'signup.html', context=context)

@login_required(login_url='login')
def add_todo(request):
    if request.user.is_authenticated:
        user = request.user
        print(user)
        form = TODOForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            todo = form.save(commit=False)
            todo.user = user
            todo.save()
            print(todo)
            return redirect("home")
        else:
            return render(request, 'index.html', context={'form': form})

def delete_todo(request, id):
    print(id)
    TODO.objects.get(pk=id).delete()
    return redirect('home')

def change_todo(request, id, status):
    todo = TODO.objects.get(pk=id)
    todo.status = status
    todo.save()
    return redirect('home')

def signout(request):
    logout(request)
    return redirect('login')

def load_todo_details(request, id):
    try:
        todo = TODO.objects.get(pk=id)
        todo_details = {
            'title': todo.title,
            'priority': todo.priority,
            'status': todo.status,
            # Add other fields as needed
        }
        return JsonResponse(todo_details)
    except TODO.DoesNotExist:
        return JsonResponse({'error': 'Todo not found'}, status=404)

@login_required(login_url='login')
def update_todo(request, id):
    print("Updated is " + str(id))
    id_str = str(id)
    todo = get_object_or_404(TODO, pk=id)
    if request.method == 'POST':
        form = TODOForm(request.POST, instance=todo)  # Correct form name
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = TODOForm(instance=todo)  # Correct form name
    return render(request, 'home.html', {'form': form, 'isEditing': True, 'todo': todo})
