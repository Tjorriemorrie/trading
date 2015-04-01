from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'binary.views.home'),
    url(r'^cron/run$', 'binary.views.run'),
    url(r'^cron/notify', 'binary.views.notify'),
    url(r'^cron/delete', 'binary.views.delete'),
)
