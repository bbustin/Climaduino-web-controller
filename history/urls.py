from django.conf.urls import patterns, url
from history import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	)