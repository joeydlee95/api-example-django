from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template.context_processors import csrf
from django.utils import timezone

import requests
import datetime
from .forms import PatientForm, DoctorForm, DemographicForm
from .models import Patient, Appointment
from django.conf import settings

# celery for async

def convert_timestamp_to_time(timestamp):
   date = datetime.datetime.strptime( timestamp, "%Y-%m-%dT%H:%M:%S")
   return timezone.make_aware(date)
   

@login_required(login_url='/login/')
def home(request):
  context = Context({'username' : request.user.username })
  return render(request, 'index.html', context)


@login_required(login_url='/login/')
def logout(request):
  auth_logout(request)
  return redirect(home)

def get_authorization(request):
  social = request.user.social_auth.get(provider='drchrono')
  access_token = social.extra_data['access_token']
  return 'Bearer %s' % access_token

def get_patient_id(request, first_name, last_name):
  headers = {
    'Authorization': get_authorization(request),
  }
  params = {
    'first_name': first_name,
    'last_name': last_name,
  }

  url = 'https://drchrono.com/api/patients_summary'
  response = requests.get(url, headers=headers, params=params)
  if response.status_code == requests.codes.ok:
    data = response.json()
    appointments = data['results']
    if appointments[0]['id']:
      return appointments[0]['id']
  return None

def get_appointment_id(request, patient_id):
  headers = {
    'Authorization': get_authorization(request),
  }
  date_today = datetime.date.today().isoformat()
  params = {
    'date': date_today,
    'patient': patient_id,
  }
  url = 'https://drchrono.com/api/appointments'
  response = requests.get(url, headers=headers, params=params)
  if response.status_code == requests.codes.ok:
    data = response.json()
    appointments = data['results']
    for appointment in appointments:
      if appointment['patient'] == patient_id:
        return appointment['id']
  return None

def get_patient_info(request, patient_id):
  headers = {
    'Authorization': get_authorization(request),
  }

  url = 'https://drchrono.com/api/patients/' + str(patient_id)
  response = requests.get(url, headers=headers)
  if response.status_code == requests.codes.ok:
    data = response.json()
    return data
  return None

def update_appointment_status(appointment_id, status):
  appointment_entry = Appointment.objects.get(appointment_id=appointment_id)
  appointment_entry.status = status
  appointment_entry.save()

def update_arrived(request, appointment_id):
  headers = {
    'Authorization': get_authorization(request),
  }
  date_today = datetime.date.today().isoformat()

  data = {
    'status': 'Arrived',
  }
  url = 'https://drchrono.com/api/appointments/' + appointment_id
  response = requests.patch(url, headers=headers, data=data)
  response.raise_for_status()

# TODO: must change all appointment with the same patient_id
def update_appointment(appointment_id, patient_id, form):
  appointment_entry = Appointment.objects.get(appointment_id=appointment_id,
                                                 patient_id=patient_id,
                                                 )
  print(appointment_entry.full_name())
  print(form['first_name'])
  print(form['last_name'])
  appointment_entry.patient_first_name = form['first_name']
  appointment_entry.patient_last_name = form['last_name']
  appointment_entry.save()
  print('updated appointment status')

def update_demographic(request, appointment_id, patient_id, form):
  headers = {
    'Authorization': get_authorization(request),
  }

  data = {
    'first_name': form['first_name'],
    'last_name': form['last_name'],
  }

  url = 'https://drchrono.com/api/patients/' + str(patient_id)
  response = requests.patch(url, headers=headers, data=data)
  response.raise_for_status()


def check_doctor_id(request, doctor_id):
  headers = {
    'Authorization': get_authorization(request),
  }

  url = 'https://drchrono.com/api/users/current'
  response = requests.get(url, headers=headers)
  if response.status_code == requests.codes.ok:
    response_doctor_id = response.json()['doctor']
    if doctor_id == str(response_doctor_id):
      return True

  return False

@login_required(login_url='/login/')
def patient_signin(request):
  if request.method == 'POST':
    form = PatientForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      try:
        patient_id = get_patient_id(request, first_name, last_name)
        appointment_id = get_appointment_id(request, patient_id)
      except IndexError:
        return redirect(patient_signin)

      patient = Patient(first_name=first_name,
                        last_name=last_name, 
                        patient_id=patient_id,
                        appointment_id=appointment_id)

      # update demographic
      return redirect(patient_demographic, patient_id=patient_id, appointment_id=appointment_id)
  else:
    form = PatientForm()
  
  context = Context({ 'form': form })
  context.update(csrf(request))
  return render(request, 'patient.html', context)

@login_required(login_url='/login/')
def patient_demographic(request, appointment_id, patient_id=None):
  if request.method == 'POST':
    form = DemographicForm(request.POST)
    if form.is_valid():
      form_data = {
        'first_name': form.cleaned_data['first_name'],
        'last_name': form.cleaned_data['last_name'],
      }
      update_demographic(request, appointment_id, patient_id, form_data)
      print('entering update')
      update_appointment(appointment_id, patient_id, form_data)
      print('exiting update')
      update_arrived(request, appointment_id)
      update_appointment_status(appointment_id,'Arrived')
      return redirect(thanks)
  else:
    patient = get_patient_info(request, patient_id)
    form = DemographicForm({ 'first_name': patient['first_name'],
                             'last_name': patient['last_name'],
                          })
    context = Context({ 'form': form, 
                        'appointment_id': appointment_id,
                        'patient_id': patient_id, })
    context.update(csrf(request))
    return render(request, 'demographic.html', context)
    #return render(request, 'thanks.html')

@login_required(login_url='/login/')
def doctor_signin(request):
  if request.method == 'POST':
    form = DoctorForm(request.POST)
    if form.is_valid():
      doctor_id = form.cleaned_data['userid']
      if check_doctor_id(request, doctor_id):
        return redirect(doctor_schedule, doctor_id=doctor_id)
      else:
        return redirect(doctor_signin)
  else:
    form = DoctorForm()
  
  context = Context({ 'form': form })
  context.update(csrf(request))
  return render(request, 'doctor.html', context)

def create_appointment(request, appointment):
  date_appointment = datetime.date.today().isoformat()
  scheduled_time = convert_timestamp_to_time(appointment['scheduled_time'])
  exam_room = appointment['exam_room']
  duration = appointment['duration']
  patient_id = appointment['patient']
  status = appointment['status']
  appointment_id = appointment['id']

  headers = {
    'Authorization': get_authorization(request),
  }

  url = 'https://drchrono.com/api/patients_summary/' + str(patient_id)
  response = requests.get(url, headers=headers)
  response.raise_for_status()
  data = response.json()
  patient = data

  patient_last_name = patient['last_name']
  patient_first_name = patient['first_name']
  appointment_entry = Appointment.objects.create(date_appointment=date_appointment,
                                                 scheduled_time=scheduled_time,
                                                 exam_room=exam_room,
                                                 duration=duration,
                                                 patient_id=patient_id,
                                                 patient_first_name=patient_first_name,
                                                 patient_last_name=patient_last_name,
                                                 status=status,
                                                 appointment_id=appointment_id)


@login_required(login_url='/login/')
# TODO: Also ensure you can't access this unless you typed in id
def doctor_schedule(request, doctor_id):
  date_today = datetime.date.today().isoformat()

  headers = {
    'Authorization': get_authorization(request),
  }

  # TODO: must disable auto suggestions
  params = {
    'date': date_today,
    'doctor': doctor_id, #203468
  }

  url = 'https://drchrono.com/api/appointments'
  response = requests.get(url, headers=headers, params=params)

  response.raise_for_status()
  data = response.json()
  appointments = data['results']

  for appointment in appointments:
    if appointment['patient']:
      # check if there is already same appointment
      try:
        appointment_entry = Appointment.objects.get(appointment_id=appointment['id'])
        # update status should happen at patient checkin
        
      except Appointment.DoesNotExist:
        create_appointment(request, appointment)

  context = Context({ 'appointments' : Appointment.objects.all().filter(date_appointment=date_today,
                                                                        is_archived=False,) })

  # query patient with id: 71162354
  # make time into viewable time: 2018-01-13T09:00:00
  return render(request, 'schedule.html', context)
  

@login_required(login_url='/login/')
def thanks(request):
  return render(request, 'thanks.html')