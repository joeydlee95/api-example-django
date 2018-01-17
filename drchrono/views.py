from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template.context_processors import csrf
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View, FormView
from django.views.generic.list import ListView

import requests
import datetime
from drchrono import helper # bad practice for app import?
from .forms import PatientForm, DoctorForm, DemographicForm
from .models import Patient, Appointment
from django.conf import settings
from django.views.decorators.http import require_http_methods

# celery for async


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class HomeView(LoginRequiredMixin, View):
  template_name = 'index.html'

  def get(self, request, *args, **kwargs):
    return render(request, self.template_name)


class PatientView(LoginRequiredMixin, FormView):
  template_name = 'patient.html'
  form_class = PatientForm

  def get(self, request, *args, **kwargs):
    form = self.form_class()
    context = Context({ 'form': form })
    context.update(csrf(request))
    return render(request, self.template_name, context)

  def post(self, request, *args, **kwargs):
    form = self.form_class(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']

      patient_id = self.handle_patient_id(request, first_name, last_name)
      if not patient_id:
        return self.get(request)

      appointment_id = self.handle_appointment_id(request, patient_id)
      if not appointment_id:
        return self.get(request)

      redirecturl = '/demographic/' + str(appointment_id) + '/' + str(patient_id)
      return redirect(redirecturl)
      #return redirect(patient_demographic, patient_id=patient_id, appointment_id=appointment_id)

  def handle_patient_id(self, request, first_name, last_name):
    try:
        patient_id = helper.get_patient_id(request, first_name, last_name)
    except IndexError:
        # TODO: include error message, cannot find you in files
        return None

    if patient_id:
        return patient_id
    else:
        return None

  def handle_appointment_id(self, request, patient_id):
    try:
      appointment_id = helper.get_appointment_id(request, patient_id)
    except IndexError:
      # TODO: include error message, no appointments today
      return None

    if appointment_id:
      return appointment_id
    else:
      return None


class DemographicView(LoginRequiredMixin, FormView):
  template_name = 'patient.html'
  form_class = DemographicForm

  def get(self, request, *args, **kwargs):
    patient_id = self.kwargs['patient_id']
    appointment_id = self.kwargs['appointment_id']

    patient = helper.get_patient_info(request, patient_id)
    form = self.form_class({ 'first_name': patient['first_name'],
                             'last_name': patient['last_name'],
                          })

    context = Context({ 'form': form, 
                        'appointment_id': appointment_id,
                        'patient_id': patient_id, })

    context.update(csrf(request))
    return render(request, 'demographic.html', context)

  def post(self, request, *args, **kwargs):
    patient_id = self.kwargs['patient_id']
    appointment_id = self.kwargs['appointment_id']

    form = self.form_class(request.POST)
    if form.is_valid():
      form_data = {
        'first_name': form.cleaned_data['first_name'],
        'last_name': form.cleaned_data['last_name'],
      }
      update_patient_status = helper.update_demographic(request, appointment_id, patient_id, form_data)
      if update_patient_status:
        self.update_appointment(appointment_id, patient_id, form_data)

      update_arrival_status = helper.update_arrived(request, appointment_id)
      if update_arrival_status:
        status = 'Arrived'
        self.update_appointment_status(appointment_id, status)

      return redirect(thanks)

  def update_appointment_status(self, appointment_id, status):
    appointment_entry = Appointment.objects.get(appointment_id=appointment_id)
    appointment_entry.status = status
    appointment_entry.checkin_time = timezone.now()
    appointment_entry.save()

  # TODO: must change all appointment with the same patient_id
  def update_appointment(self, appointment_id, patient_id, form):
    appointment_entry = Appointment.objects.get(appointment_id=appointment_id,
                                                   patient_id=patient_id,
                                                )
    appointment_entry.patient_first_name = form['first_name']
    appointment_entry.patient_last_name = form['last_name']
    appointment_entry.save()


class DoctorView(LoginRequiredMixin, FormView):
  form_class = DoctorForm
  template_name = 'doctor.html'

  def get(self, request, *args, **kwargs):
    form = self.form_class()
    context = Context({ 'form': form })
    context.update(csrf(request))
    return render(request, self.template_name, context)

  def post(self, request, *args, **kwargs):
    form = DoctorForm(request.POST)
    if form.is_valid():
      doctor_id = form.cleaned_data['userid']
      if helper.check_doctor_id(request, doctor_id):
        redirecturl = '/schedule/' + str(doctor_id)
        return redirect(redirecturl)
      else:
        return self.get(request)


class DoctorScheduleList(LoginRequiredMixin, ListView):
  template_name = 'schedule.html'
  model = Appointment

  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    date_today = datetime.date.today()
    context = super(DoctorScheduleList, self).get_context_data(**kwargs)
    # Add in a QuerySet of all the books
    appointments = Appointment.objects.all()
    context['appt_list'] = appointments.filter(date_appointment=date_today,
                                               is_archived=False,
                                               doctor_id=self.kwargs['doctor_id'])
    print(context['appt_list'])
    return context

  def post(self, request, *args, **kwargs):
    patient_clicked = request.POST.get('appointment_id')
    response_data = {}
    # before this there should be a javascript confirmation
    # check if there is already a currently beeing seen patient
      # if so, not currently seen anymore, archive them 

    # stop wait time and is currently seeing
    self.archive_currently_seeing()

    self.add_currently_seeing(patient_clicked)


    return JsonResponse({'success': 'Product created'})

  def archive_currently_seeing(self):
    try:
      appointment_entry = Appointment.objects.get(is_currently_seen=True)
      appointment_entry.is_currently_seen = False
      appointment_entry.is_archived = True
      appointment_entry.save()
    except Appointment.DoesNotExist:
      pass

  def add_currently_seeing(self, appointment_id):
    try:
      appointment_entry = Appointment.objects.get(appointment_id=appointment_id)
      appointment_entry.is_currently_seen = True
      # TODO: negative time delta
      appointment_entry.wait_time = timezone.now() - appointment_entry.scheduled_time
      appointment_entry.save()
    except Appointment.DoesNotExist:
      pass

@login_required(login_url='/login/')
def logout(request):
  auth_logout(request)
  return redirect(home)



# TODO: create patients and flush them daily?
class DailyUpdateView(LoginRequiredMixin, View):
  template_name = 'index.html'

  def get(self, request, *args, **kwargs):
    # Get appointments for the day
      # using patient id's create patient models
      # foreign key appointment to 1 patient
    if self.update_appointments(request):
      return render(request, self.template_name)
    else:
      return redirect('/update/')
  
  def update_appointments(self, request):
    """Archive old appointments and import new ones"""
    self.archive_old_appointments(request)

    data = helper.today_appointment_list(request)
    return self.setup_appointment_model(request, data)

  def archive_old_appointments(self, requests):
    today_date = datetime.date.today()
    try:
      appointment_entry = Appointment.objects.all().filter(is_archived=False)

      for appointment in appointment_entry:
        if appointment.date_appointment < today_date:
          appointment.is_archived = True
          appointment.save()
    except Appointment.DoesNotExist:
      pass

  def setup_appointment_model(self, request, data):
    if data:
      appointments = data

      for appointment in appointments:
        # Break time is null
        if appointment['patient']:
          try:
            appointment_entry = Appointment.objects.get(appointment_id=appointment['id'])
            
          except Appointment.DoesNotExist:
            self.add_appointment_model(request, appointment)

      return True
    return False

  def add_appointment_model(self, request, appointment):
    model_data = {
      'date_appointment': datetime.date.today().isoformat(),
      'scheduled_time': self.convert_timestamp_to_time(appointment['scheduled_time']),
      'exam_room': appointment['exam_room'],
      'duration': appointment['duration'],
      'doctor_id': appointment['doctor'],
      'patient_id': appointment['patient'],
      'status' : appointment['status'],
      'appointment_id': appointment['id'],
    }

    data = helper.get_patient_summary(request, model_data['patient_id'])
    return self.commit_appointment_model(patient=data, model_data=model_data)

  def commit_appointment_model(self, patient, model_data):
    date_appointment = model_data['date_appointment']
    scheduled_time = model_data['scheduled_time']
    exam_room = model_data['exam_room']
    duration = model_data['duration']
    doctor_id = model_data['doctor_id']
    patient_id = model_data['patient_id']
    patient_last_name = patient['last_name']
    patient_first_name = patient['first_name']
    status = model_data['status']
    appointment_id = model_data['appointment_id']

    appointment_entry = Appointment.objects.create(date_appointment=date_appointment,
                                                   scheduled_time=scheduled_time,
                                                   exam_room=exam_room,
                                                   duration=duration,
                                                   doctor_id=doctor_id,
                                                   patient_id=patient_id,
                                                   patient_first_name=patient_first_name,
                                                   patient_last_name=patient_last_name,
                                                   status=status,
                                                   appointment_id=appointment_id)

  def convert_timestamp_to_time(self, timestamp):
    date = datetime.datetime.strptime( timestamp, "%Y-%m-%dT%H:%M:%S")
    return timezone.make_aware(date)


@login_required(login_url='/login/')
def thanks(request):
  return render(request, 'thanks.html')