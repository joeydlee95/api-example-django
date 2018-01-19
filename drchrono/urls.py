from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views

import views
from drchrono.views import HomeView, PatientView
from drchrono.views import DemographicView, DoctorView
from drchrono.views import DoctorScheduleList, DailyUpdateView


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^update/$', DailyUpdateView.as_view(), name='update'),
    url(r'^patient/$', PatientView.as_view(), name='patient'),
    url(r'^demographic/(?P<appointment_id>\w+?)/(?P<patient_id>\w+?)$',
        DemographicView.as_view()),
    url(r'^doctor/$', DoctorView.as_view(), name='doctor'),
    url(r'^schedule/(?P<doctor_id>\w+?)/$', DoctorScheduleList.as_view(),
        name='schedule'),
    url(r'^scheduleupdate/(?P<doctor_id>\w+?)/$', views.schedule_json,
        name='schedule_update'),
    url(r'^averagewait/(?P<doctor_id>\w+?)/$', views.average_wait_time,
        name='average_wait'),
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^login/$', auth_views.login, name='login'),
]
