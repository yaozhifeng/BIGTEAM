from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('commits.views',
    url(r'^$', 'home', name='home'),
    url(r'^project/(?P<project_id>\d+)/$', 'project', name='project'),
    url(r'^person/(?P<person_id>\d+)/$', 'person', name='person'),
)

urlpatterns += patterns('commits.ajaxviews',
    url(r'^ajax/graph/summary/$', 'overall_commits', name='overall_commits'),
    url(r'^ajax/graph/project/$', 'project_commits', name='project_commits'),
    url(r'^ajax/graph/person/$', 'person_commits', name='person_commits'),
    url(r'^ajax/commits/detail/$', 'commits_detail', name='commits_detail'),
    url(r'^ajax/commits/stats/$', 'commits_stats', name='commits_stats'),

)
