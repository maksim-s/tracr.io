from django.conf.urls import patterns

urlpatterns = patterns('frontpage.views',
    (r'^$', 'index'),
    )

