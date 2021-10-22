from .models import FeedBack
from django import forms
import datetime

class FeedBackForm(forms.ModelForm):
        
    def __init__(self, *args, **kwargs):
        super(FeedBackForm, self).__init__(*args, **kwargs)
        ## add a "form-control" class to each form input
        ## for enabling bootstrap
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',})
            if name in ['Name', 'Email']:
                self.fields[name].label += " (Optional)" 
                self.fields[name].widget.attrs.update({'class': 'form-control form-control-sm',})
            elif name in ['FeedBack']:
                self.fields[name].widget.attrs.update({'class': 'form-control form-control-md',})

    class Meta:
        model = FeedBack
        fields = ("Name","Email","FeedBack")