from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm

from app.models import TODO
class TODOForm(ModelForm):
    class Meta:
        model = TODO
        fields = ['title' , 'status' , 'priority']

        # Customize labels for each field
        labels = {
                'title': 'Enter Your Note:',
                'status': 'Note Status:',
                'priority': 'Priority Level:',
                # Add or remove labels for other fields as needed
            }

class CustomUserCreationForm(UserCreationForm):
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match. Please enter the same password in both fields.")

        return cleaned_data