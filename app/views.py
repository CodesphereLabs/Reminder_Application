from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginUser, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.forms import TODOForm, CustomUserCreationForm  # Correct import
from app.models import TODO
import requests
import re

@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user).order_by('priority')
        reminders = []

        try:
            count = 0
            for todo in todos:
                events_data = todo.event.split(',')
                
                for index, event_data in enumerate(events_data, start=1):
                    match = re.match(
                            r"Event\s*:\s*(.*?)\s*Venue\s*:\s*(.*?)\s*Date\s*:\s*(.*?)\s*Time\s*:\s*(\d{1,2}.\d{2}\s*[ap]m)\s*",
                            event_data.strip())
                    if match:
                        title = match.group(1)
                        venue = match.group(2)
                        date = match.group(3)
                        time = match.group(4)  # Correctly capture the time
                        count += 1
                        reminders.append({
                            'title': title,
                            'venue': venue,
                            'date': date,
                            'time': time,  # Include the time in the reminder
                            'reminder_number': f'Reminder {count}'
                        })

            print(reminders)  # Print reminders (for debugging purposes)
        except TODO.DoesNotExist:
            return JsonResponse({'error': 'Todo not found'}, status=404)

        return render(request, 'index.html', context={'form': form, 'todos': todos, 'reminders': reminders})
    else:
        return redirect('login')  

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
            todo_text = todo.title

            flask_endpoint = 'http://127.0.0.1:5001/extract-todo-info'
            
            data = {'todo_text': todo_text}
            response = requests.post(flask_endpoint, json=data)
            if response.status_code == 200:
                event_info = response.json().get('event_info', [])
                if isinstance(event_info, list):  # Check if event_info is a list
                    event_info_str = ', '.join([f"Event: {info['Title']} Venue: {info['Venue']} Date: {info['Date']} Time: {info['Time']}" for info in event_info])
                else:
                    event_info_str = event_info  # If event_info is a string, use it directly
                todo.event = event_info_str
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
    print("Hellooooooo")
    try:
        todo = TODO.objects.get(pk=id)
        todo_details = {
            'title': todo.title,
            'priority': todo.priority,
            'status': todo.status,
            'event': todo.event,
            # Add other fields as needed
        }
        print(todo_details)
        return JsonResponse(todo_details)
    except TODO.DoesNotExist:
        return JsonResponse({'error': 'Todo not found'}, status=404)

def load_all_todo_details(request):
    try:
        todos = TODO.objects.all()
        todo_details_list = []
        for todo in todos:
            todo_details = {
                'title': todo.title,
                'priority': todo.priority,
                'status': todo.status,
                'event': todo.event,
                # Add other fields as needed
            }
            todo_details_list.append(todo_details)
        return JsonResponse(todo_details_list, safe=False)
    except TODO.DoesNotExist:
        return JsonResponse({'error': 'No todos found'}, status=404)

@login_required(login_url='login')
def update_todo(request, id):
    todo = get_object_or_404(TODO, pk=id)
    if request.method == 'POST':
        form = TODOForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user  # Ensure the user is set
            todo_text = todo.title
            flask_endpoint = 'http://127.0.0.1:5001/extract-todo-info'
            data = {'todo_text': todo_text}
            response = requests.post(flask_endpoint, json=data)
            if response.status_code == 200:
                event_info = response.json().get('event_info', [])
                if isinstance(event_info, list):
                    event_info_str = ', '.join([f"Event: {info['Title']} Venue: {info['Venue']} Date: {info['Date']} Time: {info['Time']}" for info in event_info])
                else:
                    event_info_str = event_info
                todo.event = event_info_str
                todo.save()
                return redirect("home")
    else:
        form = TODOForm(instance=todo)
    return render(request, 'home.html', {'form': form, 'isEditing': True, 'todo': todo})