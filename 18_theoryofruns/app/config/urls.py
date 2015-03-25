from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'binary.views.home'),
    url(r'^cron/run$', 'binary.views.run'),
)
