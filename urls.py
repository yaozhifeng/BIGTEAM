from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'commits.views.home', name='home'),
    url(r'^project/(?P<project_id>\d+)/$', 'commits.views.project', name='project'),
    url(r'^person/(?P<person_id>\d+)/$', 'commits.views.person', name='person'),
    url(r'^ajax/summary/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.summary', name='summary'),
    url(r'^ajax/summary/project/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.project_summary', name='project_summary'),
    url(r'^ajax/detail/project/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.project_detail', name='project_detail'),
    # url(r'^bigteam/', include('bigteam.foo.urls')),
    # url(r'^$', 'commits.views.home', name='home'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
