from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template.context_processors import csrf

import requests
from datetime import date
from .forms import PatientForm, DoctorForm


@login_required(login_url='/login/')
def home(request):
  context = Context({'username' : request.user.username })
  return render(request, 'index.html', context)


@login_required(login_url='/login/')
def logout(request):
  auth_logout(request)
  return redirect(home)


@login_required(login_url='/login/')
def patient_signin(request):
  if request.method == 'POST':
    form = PatientForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      return redirect(thanks)
  else:
    form = PatientForm()
  
  context = Context({ 'form': form })
  context.update(csrf(request))
  return render(request, 'patient.html', context)

@login_required(login_url='/login/')
def doctor_signin(request):
  if request.method == 'POST':
    form = DoctorForm(request.POST)
    if form.is_valid():
      userid = form.cleaned_data['userid']
      return redirect(doctor_schedule)
  else:
    form = DoctorForm()
  
  context = Context({ 'form': form })
  context.update(csrf(request))
  return render(request, 'doctor.html', context)
  # need to have doctor signin with another identification

@login_required(login_url='/login/')
def doctor_schedule(request):
  social = request.user.social_auth.get(provider='drchrono')
  access_token = social.extra_data['access_token']

  authorization = 'Bearer %s' % access_token
  date_today = date.today().isoformat()

  headers = {
    'Authorization': authorization,
  }

  params = {
    'date': date_today,
    'doctor': '203468', #hardcoded for now
  }

  response = requests.get('https://drchrono.com/api/appointments', headers=headers, params=params)

  response.raise_for_status()
  data = response.json()
  appointments = data['results']

  params2 = {
    'doctor': '203468',
  }

  patients = []
  patients_url = 'https://drchrono.com/api/patients_summary'
  while patients_url:
      data = requests.get(patients_url, headers=headers, params=params2).json()
      patients.extend(data['results'])
      patients_url = data['next'] # A JSON null on the last page

  for appointment in appointments:
    for patient in patients:
      if appointment['patient'] == patient['id']:
        appointment['full_name'] = patient['first_name'] + ' ' + patient['last_name']



  context = Context({ 'appointments' : appointments })

  # query patient with id: 71162354
  # make time into viewable time: 2018-01-13T09:00:00
  return render(request, 'schedule.html', context)
  

@login_required(login_url='/login/')
def thanks(request):
  return render(request, 'thanks.html')