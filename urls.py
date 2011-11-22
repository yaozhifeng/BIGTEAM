from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import django_cron
django_cron.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'commits.views.home', name='home'),
    url(r'^project/(?P<project_id>\d+)/$', 'commits.views.project', name='project'),
    url(r'^person/(?P<person_id>\d+)/$', 'commits.views.person', name='person'),
    url(r'^ajax/graph/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.overall_summary', name='summary_graph'),
    url(r'^ajax/graph/project/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.project_summary', name='project_summary_graph'),
    url(r'^ajax/detail/project/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.project_detail', name='project_detail_graph'),
    url(r'^ajax/detail/person/(?P<person_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.person_detail', name='person_detail_graph'),
    url(r'^ajax/commits/(?P<year>\d+)/(?P<month>\d+)/$', 'commits.ajaxviews.commits_detail', name='commits_detail'),
    url(r'^ajax/commits/$', 'commits.ajaxviews.coder_commits', name='commits_stats'),
    # url(r'^bigteam/', include('bigteam.foo.urls')),
    # url(r'^$', 'commits.views.home', name='home'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
