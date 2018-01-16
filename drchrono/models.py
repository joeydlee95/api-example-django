from django.db import models
from django.conf import settings

from datetime import date
#from localflavor.us.forms import USSocialSecurityNumberField

MAX_NAME_LENGTH = settings.MAX_NAME_LENGTH

# Create your models here.
'''class Doctor(models.Model):
  doctor_id = models.AutoField(primary_key=True)
  last_name = models.CharField(max_length=MAX_NAME_LENGTH)
  first_name = models.CharField(max_length=MAX_NAME_LENGTH)
'''
class Patient(models.Model):
  last_name = models.CharField(max_length=MAX_NAME_LENGTH)
  first_name = models.CharField(max_length=MAX_NAME_LENGTH)
  patient_id = models.CharField(max_length=MAX_NAME_LENGTH)
  appointment_id = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)

  def __unicode__(self):
    return "%s %s" % (self.first_name, self.last_name)
  #ssn = USSocialSecurityNumberField()

class Appointment(models.Model):
  date_appointment = models.DateField()
  scheduled_time =  models.DateTimeField()
  exam_room = models.IntegerField()
  duration = models.IntegerField()
  patient_id = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
  patient_first_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
  patient_last_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=True, null=True)
  appointment_id = models.CharField(max_length=MAX_NAME_LENGTH)

  checkin_time = models.DateTimeField(blank=True, null=True)
  wait_time = models.DateTimeField(blank=True, null=True)
  status = models.CharField(max_length=MAX_NAME_LENGTH)

  is_archived = models.BooleanField(default=False)
  is_currently_seen = models.BooleanField(default=False)

  def full_name(self):
    return self.patient_first_name + ' ' + self.patient_last_name

  def __unicode__(self):
    return "%s %s" % (self.patient_first_name, self.patient_last_name)
