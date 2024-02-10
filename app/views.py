from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as loginUser, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.forms import TODOForm, CustomUserCreationForm  # Correct import
from django.db import transaction
from app.models import TODO
import joblib
import re

@login_required(login_url='login')
def home(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm()
        todos = TODO.objects.filter(user=user).order_by('priority')
        reminders = []  # Initialize reminders list

        try:
            for todo in todos:
                if todo.event:  # Check if event is not None
                    events_data = todo.event.split(',')
                    for event_data in events_data:
                        match = re.match(
                            r"Event\s*:\s*(.*?)\s*Venue\s*:\s*(.*?)\s*Date\s*:\s*(.*?)\s*Time\s*:\s*(\d{2}.\d{2}\s*[ap]m)\s*",
                            event_data.strip())
                        if match:
                            title = match.group(1).strip()
                            venue = match.group(2).strip()
                            date = match.group(3).strip()
                            time = match.group(4).strip()
                            reminders.append({
                                'title': title,
                                'venue': venue,
                                'date': date,
                                'time': time,
                                'reminder_number': f'Reminder{len(reminders) + 1}'
                            })

            print(reminders)  # Print reminders (for debugging purposes)
        except TODO.DoesNotExist:
            return JsonResponse({'error': 'Todo not found'}, status=404)

        return render(request, 'index.html', context={'form': form, 'todos': todos, 'reminders': reminders})


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
                        messages.error(
                            request, 'The two passwords fields didn’t match.')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'signup.html', context)

# @login_required(login_url='login')
# def add_todo(request):
#     if request.user.is_authenticated:
#         nlp_model = joblib.load("saveModels\model.joblib")
#         user = request.user
#         form = TODOForm(request.POST)
#         if form.is_valid():
#             todo = form.save(commit=False)
#             todo.user = user
#             todo.save()
#             return redirect("home")
#         else:
#             return render(request, 'index.html', context={'form': form})

@login_required(login_url='login')
def add_todo(request):
    if request.user.is_authenticated:
        user = request.user
        form = TODOForm(request.POST)
        if form.is_valid():
            # Get the title input from the form
            title = form.cleaned_data['title']
            
            # Create an instance of the ExtractFromToDo class
            extractor = joblib.load('saveModels\model.joblib')
            
            # Extract event information from the title
            event_info_list = extractor.extract_info_from_sentence(title)
            
            # Extracting the first event info from the list
            event_info = event_info_list[0] if event_info_list else {}
            
            # Create a string representation of the event information
            event_string = f"Event: {event_info.get('Title', '')}, Venue: {event_info.get('Venue', '')}, Date: {event_info.get('Date', '')}, Time: {event_info.get('Time', '')}"
            
            # Save the event information to the 'event' field of the TODO object
            todo = form.save(commit=False)
            todo.user = user
            todo.event = event_string
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
            'event': todo.event,
            # 'location': todo.location,
            # 'event_date': todo.event_date,
            # 'event_time': todo.event_time,
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
            'event': todo.event,
            # 'location': todo.location,
            # 'event_date': todo.event_date,
            # 'event_time': todo.event_time,
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
