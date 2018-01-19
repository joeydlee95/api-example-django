from django.db import models
from django.conf import settings
import pytz
import datetime
# from localflavor.us.forms import USSocialSecurityNumberField

MAX_NAME_LENGTH = settings.MAX_NAME_LENGTH
MAX_ID_LENGTH = settings.MAX_ID_LENGTH

class Patient(models.Model):
    """A model for a patient"""
    patient_id = models.CharField(primary_key=True, max_length=MAX_ID_LENGTH)
    first_name = models.CharField(max_length=MAX_NAME_LENGTH)
    last_name = models.CharField(max_length=MAX_NAME_LENGTH)
    # ssn = USSocialSecurityNumberField()

    #@classmethod
    #def create(cls, patient_id, first_name, last_name):
    #    patient = cls(patient_id=patient_id, first_name=first_name, last_name=last_name)
    #    return patient

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Appointment(models.Model):
    """A Model for an appointment."""
    appointment_id = models.CharField(max_length=MAX_ID_LENGTH)
    date_appointment = models.DateField()
    scheduled_time = models.DateTimeField()
    exam_room = models.IntegerField()
    duration = models.IntegerField()
    doctor_id = models.CharField(max_length=MAX_NAME_LENGTH,
                                 blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    checkin_time = models.DateTimeField(blank=True, null=True)
    wait_time = models.DurationField(blank=True, null=True)
    status = models.CharField(max_length=MAX_NAME_LENGTH, null=True)

    is_archived = models.BooleanField(default=False)
    is_currently_seen = models.BooleanField(default=False)

    def full_name(self):
        return str(self.patient)

    def __unicode__(self):
        return "%s" % (self.appointment_id)

    def get_readable_scheduled_time(self):
        date = self.scheduled_time.astimezone(pytz.timezone('US/Pacific'))
        return date.strftime("%Y-%m-%d %I:%M %p")

    def get_readable_checkin_time(self):
        if self.checkin_time:
            date = self.checkin_time.astimezone(pytz.timezone('US/Pacific'))
            checkin_time = date.strftime("%Y-%m-%d %I:%M %p")
        else:
            checkin_time = ""
        return checkin_time

    def get_wait_time(self):
        if self.wait_time:
            wait_time = self.wait_time
        else:
            wait_time = None
        return wait_time
