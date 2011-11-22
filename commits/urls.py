from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('commits.views',
    url(r'^$', 'home', name='home'),
    url(r'^project/(?P<project_id>\d+)/$', 'project', name='project'),
    url(r'^person/(?P<person_id>\d+)/$', 'person', name='person'),
)

urlpatterns += patterns('commits.ajaxviews',
    url(r'^ajax/graph/(?P<year>\d+)/(?P<month>\d+)/$', 'overall_summary', name='summary_graph'),
    url(r'^ajax/graph/project/(?P<year>\d+)/(?P<month>\d+)/$', 'project_summary', name='project_summary_graph'),
    url(r'^ajax/detail/project/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'project_detail', name='project_detail_graph'),
    url(r'^ajax/detail/person/(?P<person_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', 'person_detail', name='person_detail_graph'),
    url(r'^ajax/commits/(?P<year>\d+)/(?P<month>\d+)/$', 'commits_detail', name='commits_detail'),
    url(r'^ajax/commits/$', 'coder_commits', name='commits_stats'),

)
