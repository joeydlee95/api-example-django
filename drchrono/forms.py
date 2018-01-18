from django import forms
from django.conf import settings
#from localflavor.us.forms import USSocialSecurityNumberField

MAX_NAME_LENGTH = settings.MAX_NAME_LENGTH
MAX_ID_LENGTH = settings.MAX_ID_LENGTH

class PatientForm(forms.Form):
    first_name = forms.CharField(label='Your first name', max_length=MAX_NAME_LENGTH)
    last_name = forms.CharField(label='Your last name', max_length=MAX_NAME_LENGTH)
    #ssn = USSocialSecurityNumberField()

class DoctorForm(forms.Form):
    userid = forms.CharField(label='Your id', max_length=MAX_ID_LENGTH)

class DemographicForm(forms.Form):
    
    first_name = forms.CharField(label='First name', max_length=MAX_NAME_LENGTH, initial=True)
    last_name = forms.CharField(label='Last name', max_length=MAX_NAME_LENGTH, initial=True)
    #others 