from django.db import models
from django.conf import settings

import datetime
#from localflavor.us.forms import USSocialSecurityNumberField

MAX_NAME_LENGTH = settings.MAX_NAME_LENGTH

# Create your models here.
'''class Doctor(models.Model):
  doctor_id = models.AutoField(primary_key=True)
  last_name = models.CharField(max_length=MAX_NAME_LENGTH)
  first_name = models.CharField(max_length=MAX_NAME_LENGTH)
'''
class Patient(models.Model):
  patient_id = models.CharField(primary_key=True, max_length=MAX_NAME_LENGTH)
  first_name = models.CharField(max_length=MAX_NAME_LENGTH)
  last_name = models.CharField(max_length=MAX_NAME_LENGTH)

  def __unicode__(self):
    return "%s %s" % (self.first_name, self.last_name)
  #ssn = USSocialSecurityNumberField()


class Appointment(models.Model):
  appointment_id = models.CharField(max_length=MAX_NAME_LENGTH)
  date_appointment = models.DateField()
  scheduled_time =  models.DateTimeField()
  exam_room = models.IntegerField()
  duration = models.IntegerField()
  doctor_id = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
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
    return self.scheduled_time.strftime("%Y-%m-%d %I:%M %p")

  def get_readable_checkin_time(self):
    if self.checkin_time:
      checkin_time = self.checkin_time.strftime("%Y-%m-%d %I:%M %p")
    else:
      return ""

