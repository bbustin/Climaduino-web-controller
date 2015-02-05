from django.conf.urls import patterns, url
from history import views

urlpatterns = patterns('',
	url(r'^([A-Za-z0-9]*)$', views.index, name='index'),
	)