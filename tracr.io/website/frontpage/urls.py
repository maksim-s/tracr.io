from django.conf.urls import patterns

urlpatterns = patterns('frontpage.views',
    (r'^$', 'index'),
    (r'^thank-you/$', 'thank_you'),
    )
