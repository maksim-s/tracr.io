from django.conf.urls import patterns

urlpatterns = patterns('myapp.views',
    (r'^$', 'index'),
    )

