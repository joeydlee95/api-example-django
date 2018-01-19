from django import forms
from django.conf import settings
# from localflavor.us.forms import USSocialSecurityNumberField


MAX_NAME_LENGTH = settings.MAX_NAME_LENGTH
MAX_ID_LENGTH = settings.MAX_ID_LENGTH


class PatientForm(forms.Form):
    first_name = forms.CharField(label='Your first name',
                                 max_length=MAX_NAME_LENGTH)
    last_name = forms.CharField(label='Your last name',
                                max_length=MAX_NAME_LENGTH)
    # ssn = USSocialSecurityNumberField()


class DoctorForm(forms.Form):
    userid = forms.CharField(label='Your id', max_length=MAX_ID_LENGTH)


class DemographicForm(forms.Form):
    gender_choices = (
                        ('Male', 'Male'),
                        ('Female', 'Female'),
                        ('Other', 'Other'),
                     )
    gender = forms.ChoiceField(label='Gender', choices=gender_choices,
                               initial=True)
    email = forms.CharField(label='Email', required=False, max_length=254,
                            initial=True)

    # others
