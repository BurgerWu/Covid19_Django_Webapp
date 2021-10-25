from .models import FeedBack
from django import forms
import datetime

class FeedBackForm(forms.ModelForm):
    """Create feedback form instance for feednack input in the webpage"""   
    def __init__(self, *args, **kwargs):
        super(FeedBackForm, self).__init__(*args, **kwargs)
        ##Add a "form-control" class to each form input for enabling bootstrap
        for name in self.fields.keys():
            #Add form-control class to form fields
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})
            #Add optional text for Name and Email field
            if name in ['Name', 'Email']:
                self.fields[name].label += " (Optional)" 
                self.fields[name].widget.attrs.update({'class': 'form-control form-control-sm',})
            elif name in ['FeedBack']:
                self.fields[name].widget.attrs.update({'class': 'form-control form-control-md',})

    class Meta:
        #Declare model and field linked to the form
        model = FeedBack
        fields = ("Name","Email","FeedBack")