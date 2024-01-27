from django.forms import ModelForm

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