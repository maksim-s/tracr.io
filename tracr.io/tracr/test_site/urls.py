from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^', include('myapp.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
