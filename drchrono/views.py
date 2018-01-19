from django.shortcuts import redirect, render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template.context_processors import csrf
from django.utils import timezone
from django.http import JsonResponse


from django.views.generic import View, FormView
from django.views.generic.list import ListView

import datetime
from drchrono import helper
from .forms import PatientForm, DoctorForm, DemographicForm
from .models import Patient, Appointment


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
        context = Context({'form': form})
        context.update(csrf(request))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # This get assumes that you only have 1 entry
            patient = self.patient_safe_get(first_name=first_name,
                                            last_name=last_name)
            if not patient:
                return self.get(request)

            appointment_id = self.handle_appointment_id(request,
                                                        patient)
            if not appointment_id:
                return self.get(request)

            appt_end = str(appointment_id)
            patient_end = str(patient.patient_id)

            redirecturl = '/demographic/' + appt_end + '/' + patient_end
            return redirect(redirecturl)

    def patient_safe_get(self, first_name, last_name):
        try:
            patient = Patient.objects.get(first_name__iexact=first_name,
                                          last_name__iexact=last_name)
        except Patient.DoesNotExist:
            patient = None
        return patient

    def handle_appointment_id(self, request, patient):
        try:
            #appointment_id = helper.get_appointment_id(request,
                                                       #str(patient_id))
            appointment = Appointment.objects.filter(is_archived=False,
                                                     patient=patient,
                                                     is_currently_seen=False, )
            appointment_id = appointment[0].appointment_id
        except IndexError:
            appointment_id = None

        return appointment_id


class DemographicView(LoginRequiredMixin, FormView):
    template_name = 'patient.html'
    form_class = DemographicForm

    def get(self, request, *args, **kwargs):
        patient_id = self.kwargs['patient_id']
        appointment_id = self.kwargs['appointment_id']

        patient = helper.get_patient_info(request, patient_id)
        if not patient:
            print("Could not get patient %s info." % patient_id)
            return redirect('patient')
        form = self.form_class({'email': patient['email'],
                                'gender': patient['gender'], })

        context = Context({'form': form,
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
              'email': form.cleaned_data['email'],
              'gender': form.cleaned_data['gender'],
            }
            # Better error message should go here
            patient_status = helper.update_demographic(request,
                                                       patient_id, form_data)

            update_arrival_status = helper.update_arrived(request,
                                                          appointment_id)
            if update_arrival_status:
                status = 'Arrived'
                self.update_appointment_status(appointment_id, status)

            return redirect(thanks)

    def update_appointment_status(self, appointment_id, status):
        appointment_entry = Appointment.objects.get(appointment_id=appointment_id)
        appointment_entry.status = status
        appointment_entry.checkin_time = timezone.now()
        appointment_entry.save()


class DoctorView(LoginRequiredMixin, FormView):
    form_class = DoctorForm
    template_name = 'doctor.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = Context({'form': form})
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


class DoctorScheduleList(LoginRequiredMixin, View):
    template_name = 'schedule.html'
    model = Appointment

    def get(self, request, *args, **kwargs):
        date_today = datetime.date.today()
        template_name = 'schedule.html'
        doctor_id = self.kwargs['doctor_id']
        context = Context({
            "template_name": "contacts/index.html",
            "queryset": Appointment.objects.all().filter(date_appointment=date_today,
                                                         is_archived=False,
                                                         doctor_id=doctor_id),
            "extra_context" : { "doctor_id" : doctor_id, }
            })

        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        patient_clicked = request.POST.get('appointment_id')
        print(patient_clicked)
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
            print("No currently seeing patient.")
            pass

    def add_currently_seeing(self, appointment_id):
        try:
            appointment_entry = Appointment.objects.get(appointment_id=appointment_id)
            appointment_entry.is_currently_seen = True

            appointment_entry.wait_time = timezone.now() - appointment_entry.checkin_time
            appointment_entry.save()
        except Appointment.DoesNotExist:
            pass
            print("Failed to get Appointment")


# TODO: create patients and flush them daily?
class DailyUpdateView(LoginRequiredMixin, View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if self.update_appointments(request):
            return render(request, self.template_name)
        else:
            print("Did not update fully. Try again.")
            return redirect('/')

    def update_appointments(self, request):
        """Archive old appointments and import new ones"""
        self.archive_old_appointments(request)

        data = helper.today_appointment_list(request)
        patient_updated = self.update_patients(request, data)
        if patient_updated:
            return self.setup_appointment_model(request, data)
        else:
            return None

    def archive_old_appointments(self, request):
        today_date = datetime.date.today()
        try:
            appointment_entry = Appointment.objects.all().filter(is_archived=False)

            for appointment in appointment_entry:
                if appointment.date_appointment < today_date:
                    appointment.is_archived = True
                    appointment.save()
        except Appointment.DoesNotExist:
            pass

    def update_patients(self, request, data):
        # patient_id from data
        if data:
            appointments = data

            for appointment in appointments:
                if appointment['patient']:
                    try:
                        patient_entry = Patient.objects.get(patient_id=appointment['patient'])
                        print("got patient, so skipping %s" % appointment['patient']) 
                    except Patient.DoesNotExist:
                        print("patient does not exist, so creating %s" % appointment['patient'])
                        patient_id = appointment['patient']
                        self.add_patient_model(request, patient_id)

            return True
        return False

    def add_patient_model(self, request, patient_id):
        data = helper.get_patient_summary(request=request, patient_id=patient_id)
        return self.commit_patient_model(request=request, patient=data)

    def commit_patient_model(self, request, patient):
        first_name = patient['first_name']
        last_name = patient['last_name']
        patient_id = patient['id']
        print("making %s" % str(patient_id))
        patient_entry = Patient.objects.create(patient_id=patient['id'],
                                       first_name=patient['first_name'],
                                       last_name=patient['last_name'], )
        return patient_entry

    def setup_appointment_model(self, request, data):
        if data:
            print("here")
            appointments = data

            for appointment in appointments:
                # Break time is null
                print("before appot")
                if appointment['patient']:
                    print("appt exists")
                    try:
                        print("start of try")
                        appointment_entry = Appointment.objects.get(appointment_id=appointment['id'])

                    except Appointment.DoesNotExist:
                        print("failed try")
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
          'status': appointment['status'],
          'appointment_id': appointment['id'],
        }
        try:
            patient = Patient.objects.get(patient_id=model_data['patient_id'])
        except Patient.DoesNotExist:
            print("This patient %s does not exist." % str(model_data['patient_id']))

        return self.commit_appointment_model(patient=patient, model_data=model_data)

    # True if committed, False if failed
    def commit_appointment_model(self, patient, model_data):
        appointment_id = model_data['appointment_id']
        date_appointment = model_data['date_appointment']
        scheduled_time = model_data['scheduled_time']
        exam_room = model_data['exam_room']
        duration = model_data['duration']
        doctor_id = model_data['doctor_id']
        status = model_data['status']

        appointment_entry = Appointment.objects.create(appointment_id=appointment_id,
                                                       date_appointment=date_appointment,
                                                       scheduled_time=scheduled_time,
                                                       exam_room=exam_room,
                                                       duration=duration,
                                                       doctor_id=doctor_id,
                                                       patient=patient,
                                                       status=status)
        return True

    def convert_timestamp_to_time(self, timestamp):
        date = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        return timezone.make_aware(date)


def schedule_json(request, doctor_id):
    if (request.is_ajax()):
        date_today = datetime.date.today()
        appointments = Appointment.objects.all().filter(is_archived=False,
                                                        doctor_id=doctor_id,
                                                        date_appointment=date_today)

        data = {}
        data['appointments'] = []
        for appointment in appointments:
            scheduled_time = appointment.get_readable_scheduled_time()
            checkin_time = appointment.get_readable_checkin_time()

            temp_data = {'appointment_id': appointment.appointment_id,
                         'scheduled_time': scheduled_time,
                         'exam_room': appointment.exam_room,
                         'duration': appointment.duration,
                         'patient': str(appointment.patient),
                         'checkin_time': checkin_time,
                         'status': appointment.status,
                         'is_currently_seen': appointment.is_currently_seen, }

            if temp_data['checkin_time']:
                temp_wait_time = timezone.now() - appointment.checkin_time
                seconds = temp_wait_time.total_seconds()
                minutes = seconds // 60
                temp_data['wait_time'] = minutes

            data['appointments'].append(temp_data)

        data['status'] = "Success"
        try:
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'Fail'})

    else:
        return render(request, 'index.html')


def average_wait_time(request, doctor_id):
    if (request.is_ajax()):
        data = {}
        appointments = Appointment.objects.all().filter(is_archived=True,
                                                        doctor_id=doctor_id,
                                                        )
        count = 0
        total_wait_time = datetime.timedelta(0)
        for appointment in appointments:
            if appointment.get_wait_time():
                count = count + 1
                total_wait_time += appointment.get_wait_time()

        if count == 0:
            average_wait_time = 0
        else:
            average_wait_time = total_wait_time.total_seconds() // count
            average_wait_time = average_wait_time // 60

        data['wait_time'] = average_wait_time
        data['status'] = "Success"
        try:
            print(data)
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'Fail'})
    else:
        return render(request, 'index.html')


@login_required(login_url='/login/')
def logout(request):
    auth_logout(request)
    return redirect(home)


@login_required(login_url='/login/')
def thanks(request):
    return render(request, 'thanks.html')
