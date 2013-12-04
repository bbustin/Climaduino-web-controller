from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'climaduino.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'settings.views.index', name="index"), #use the index function from settings for now
    url(r'^admin/', include(admin.site.urls)),
    url(r'^settings/', include('settings.urls', namespace='settings')),
    url(r'^history/', include('history.urls', namespace='history')),
)
