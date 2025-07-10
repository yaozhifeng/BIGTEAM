from django.urls import path, include
from . import views, ajaxviews

app_name = 'commits'

urlpatterns = [
    # Main views
    path('', views.home, name='home'),
    path('project/<int:project_id>/', views.project, name='project'),
    path('person/<int:person_id>/', views.person, name='person'),
    path('update_all/', views.update_all, name='update_all'),
    
    # AJAX API endpoints
    path('ajax/graph/summary/', ajaxviews.overall_commits, name='overall_commits'),
    path('ajax/graph/project/', ajaxviews.project_commits, name='project_commits'),
    path('ajax/graph/person/', ajaxviews.person_commits, name='person_commits'),
    path('ajax/commits/detail/', ajaxviews.commits_detail, name='commits_detail'),
    path('ajax/commits/stats/', ajaxviews.commits_stats, name='commits_stats'),
    path('ajax/commits/project/', ajaxviews.commits_project, name='commits_project'),
]
