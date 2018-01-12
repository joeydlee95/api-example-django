from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import Context

import requests
import json
#from models import Doctor


@login_required(login_url='/login/')
def home(request):
  social = request.user.social_auth.get(provider='drchrono')
  access_token = social.extra_data['access_token']
  response = requests.get('https://drchrono.com/api/users/current',
                           headers={ 'Authorization': 'Bearer %s' % access_token })

  # and is you are have the option to see patient list

  #check for rate limits

  #check for deprecation
  response.raise_for_status()
  data = response.json()


  username = request.user.username
  is_doctor = data['is_doctor']

  context = Context({ 'is_doctor': is_doctor,
                      'username' : username })

  return render(request, 'index.html', context)

@login_required(login_url='/login/')
def view_patients(request):
  social = request.user.social_auth.get(provider='drchrono')
  access_token = social.extra_data['access_token']
  headers = {
    'Authorization': 'Bearer %s' % access_token,
  }

  patients = []
  patients_url = 'https://drchrono.com/api/patients_summary'
  while patients_url:
    data = requests.get(patients_url, headers=headers).json()
    patients.extend(data['results'])
    patients_url = data['next'] # A JSON null on the last page
    print(data)


  total_patients = len(patients)
  context = Context({ 'total_patients': total_patients,
                      'patients': patients })
  return render(request, 'patients.html', context)

def logout(request):
  if request.user.is_authenticated:
    auth_logout(request)
  return redirect(home)
