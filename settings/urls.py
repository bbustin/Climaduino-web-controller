from django.conf.urls import patterns, url
from settings import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^(\d{1,3})$', views.device_index, name='device_index'),
	url(r'^temperature/(\d{1,3})$', views.set_temperature, name='temperature'),
	url(r'^humidity/(\d{1,3})$', views.set_humidity, name='humidity'),
	# url(r'^mode$', views.set_mode, name='mode'),
 	url(r'^programs/(\d{1,3})$', views.programs, name='programs'),
 	url(r'^climaduino/(\d{1,3})$', views.climaduino, name='climaduino'),
    )