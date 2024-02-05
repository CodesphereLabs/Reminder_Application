from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginUser, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.forms import TODOForm, CustomUserCreationForm  # Correct import
from app.models import TODO

# @login_required(login_url='login')
# def home(request):
#     if request.user.is_authenticated:
#         user = request.user
#         form = TODOForm()
#         todos = TODO.objects.filter(user=user).order_by('priority')
#         return render(request, 'index.html', context={'form': form, 'todos': todos})
#
# def login(request):
#     if request.method == 'GET':
#         form1 = AuthenticationForm()
#         context = {
#             "form": form1
#         }
#         return render(request, 'login.html', context=context)
#     else:
#         form = AuthenticationForm(data=request.POST)
#         print(form.is_valid())
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 loginUser(request, user)
#                 return redirect('home')
#         else:
#             context = {
#                 "form": form
#             }
#             return render(request, 'login.html', context=context)
#
# def signup(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request, 'Account created successfully.')
#             return redirect('home')
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f'{field.capitalize()}: {error}')
#                     # Customize the error message for password mismatch
#                     if field == 'password2' and 'password1' in errors:
#                         messages.error(request, 'The two passwords fields didn’t match.')
#     else:
#         form = CustomUserCreationForm()
#
#     context = {'form': form}
#     return render(request, 'signup.html', context)
#
# @login_required(login_url='login')
# def add_todo(request):
#     if request.user.is_authenticated:
#         user = request.user
#         print(user)
#         form = TODOForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             todo = form.save(commit=False)
#             todo.user = user
#             todo.save()
#             print(todo)
#             return redirect("home")
#         else:
#             return render(request, 'index.html', context={'form': form})

# @login_required(login_url='login')
# def home(request):
#     if request.user.is_authenticated:
#         user = request.user
#         form = TODOForm()
#         todos = TODO.objects.filter(user=user).order_by('priority')
#
#         todo = TODO.objects.get()
#                 todo_details = {
#                     'title': todo.title,
#                     'priority': todo.priority,
#                     'status': todo.status,
#                     'event' : todo.event,
#                     'location' : todo.location,
#                     'event_date' : todo.event_date,
#                     'event_time' : todo.event_time,
#                     # Add other fields as needed
#                 }
#                 print(todo_details)
#                 return JsonResponse(todo_details)
#
#         return render(request, 'index.html', context={'form': form, 'todos': todos})

@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user).order_by('priority')

        # Assuming you want to get the first todo for the user (you may adjust the criteria)
        try:
            todo = TODO.objects.filter(user=user).order_by('priority').first()
            todo_details = {
                'title': todo.title,
                'priority': todo.priority,
                'status': todo.status,
                'event': todo.event,
                'location': todo.location,
                'event_date': todo.event_date,
                'event_time': todo.event_time,
                # Add other fields as needed
            }
            print(todo_details)
        except TODO.DoesNotExist:
            # Handle the case where no todo is found
            return JsonResponse({'error': 'No TODO found for the user'})

    return render(request, 'index.html', context={'form': form, 'todos': todos})

def login(request):
    if request.method == 'GET':
        form1 = AuthenticationForm()
        context = {"form": form1}
        return render(request, 'login.html', context=context)
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                loginUser(request, user)
                return redirect('home')
        else:
            context = {"form": form}
            return render(request, 'login.html', context=context)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully.')
            loginUser(request, user)  # Log in the user after signup
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
                    if field == 'password2' and 'password1' in errors:
                        messages.error(request, 'The two passwords fields didn’t match.')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'signup.html', context)

@login_required(login_url='login')
def add_todo(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = user
            todo.save()
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
            'event' : todo.event,
            'location' : todo.location,
            'event_date' : todo.event_date,
            'event_time' : todo.event_time,
            # Add other fields as needed
        }
        print(todo_details)
        return JsonResponse(todo_details)
    except TODO.DoesNotExist:
        return JsonResponse({'error': 'Todo not found'}, status=404)

def load_all_todo_details(request):
    try:
        todo = TODO.objects.get()
        todo_details = {
            'title': todo.title,
            'priority': todo.priority,
            'status': todo.status,
            'event' : todo.event,
            'location' : todo.location,
            'event_date' : todo.event_date,
            'event_time' : todo.event_time,
            # Add other fields as needed
        }
        print(todo_details)
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
