from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views

import views


urlpatterns = [
    url(r'^$', views.home , name='home'),
    url(r'^your-patient/$', views.patient_signin, name='patient'),
    url(r'^demographic/(?P<appointment_id>\w+?)/(?P<patient_id>\w+?)$', views.patient_demographic, name='demographic'),
    url(r'^your-doctor/$', views.doctor_signin, name='doctor'),
    #url(r'^schedule/(?P<doctor_id>\w+?)/$see-patient/$', views.see_patient),
    url(r'^schedule/(?P<doctor_id>\w+?)/$', views.doctor_schedule, name='doctor_schedule'),
    #url(r'^schedule/(?P<doctor_id>\w+?)/$see-patient/$', views.see_patient),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'login/$', auth_views.login, name='login'),
]
