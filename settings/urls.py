from django.conf.urls import patterns, url
from settings import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^([A-Za-z0-9]*)$', views.device_index, name='device_index'),
	url(r'^readings/([A-Za-z0-9]*)$', views.device_readings, name='readings'),
	url(r'^temperature/([A-Za-z0-9]*)$', views.set_temperature, name='temperature'),
	url(r'^humidity/([A-Za-z0-9]*)$', views.set_humidity, name='humidity'),
	# url(r'^mode$', views.set_mode, name='mode'),
 	url(r'^programs/([A-Za-z0-9]*)$', views.programs, name='programs'),
    )