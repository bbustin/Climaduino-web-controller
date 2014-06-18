from django.conf.urls import patterns, url
from history import views

urlpatterns = patterns('',
	url(r'^(\d{1,3})$', views.index, name='index'),
	)