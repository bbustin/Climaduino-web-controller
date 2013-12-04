from django.conf.urls import patterns, url
from settings import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^temperature$', views.set_temperature, name='temperature'),
	url(r'^humidity$', views.set_humidity, name='humidity'),
	# url(r'^mode$', views.set_mode, name='mode'),
	# url(r'^programming$', views.programming, name='programming'),
    )