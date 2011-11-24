# Create Ajax views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Sum, Count
import datetime
from models import *
from django.core import serializers
import json
import pdb

#Internal helper
#process query by params in request
def FilterParams(request, query):
    if request.REQUEST.__contains__('author'):
        query = query.filter(author=request.REQUEST['author'])
    if request.REQUEST.__contains__('year'):
        query = query.filter(time__year=request.REQUEST['year'])
    if request.REQUEST.__contains__('month'):
        query = query.filter(time__month=request.REQUEST['month'])
    if request.REQUEST.__contains__('project'):
        query = query.filter(repository=request.REQUEST['project'])

    return query

#Graph data
#ajax view for overall summary
#return list of {"date": date, "commit_count": commit_count}
#optional GET param: author, project, year, month
def overall_commits(request):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = {"date": """DATE(time)"""}
    graph = CommitLog.objects.all()
    graph = graph.extra(select=select_data).values('date').annotate(commit_count=Count('id'))

    graph = FilterParams(request, graph)

    return HttpResponse(json.dumps(list(graph)), 'application/json')

#Graph data
#ajax view for daily commits statistics
#return a list of {"repository__id", "repository__name", "date", "commit_count"}
#optional params: author, project, year, month
def project_commits(request):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = {"date": """DATE(time)"""}
    graph = CommitLog.objects.all()
    graph = graph.extra(select=select_data).values('repository__id', 'repository__name', 'date').annotate(commit_count=Count('id'))

    graph = FilterParams(request, graph)

    return HttpResponse(json.dumps(list(graph)), 'application/json')

#Graph data
#ajax view for project detail, per author contributes
#return a list of {"author__id", "auhor__account", "author__display", "date", "commit_count"}
#optional params: author, project, year, month
def person_commits(request):
    if not request.is_ajax():
        return HttpResponse(status=400)
    
    select_data = {"date": """DATE(time)"""}
    graph = CommitLog.objects.all()
    graph = graph.extra(select=select_data).values('author__account', 'author__display', 'author__id', 'date').annotate(commit_count=Count('id'))
    graph = FilterParams(request, graph)

    return HttpResponse(json.dumps(list(graph)), 'application/json')


#List data
#ajax view for recent commits
#return a list of {"repository__id", "repository__name", "auhor__id", "author__account", "author__display", "date", "time", "comment", "revision"}
#optional GET params: project, author, year, month
def commits_detail(request):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = {"date": """DATE(time)""", "time": """TIME(time)"""}
    commits = CommitLog.objects.all()
    commits = commits.extra(select=select_data)
    commits = commits.values('repository__id', 'repository__name', 'author__display', 'author__account', 'author__id', 'date', 'time', 'comment', 'revision');

    commits = FilterParams(request, commits)
    commits = commits.order_by('-date', '-time')[:20]

    return HttpResponse(json.dumps(list(commits)), 'application/json')

#List data
#ajax view for coder contributes
#return a list of {"repository__id", "repository__name", "authro__id", "author__account", "author__display", "commit_count"}
#optional GET params: author, project, author, month, year
def commits_stats(request):
    if not request.is_ajax():
        return HttpResponse(status=400)

    commits = CommitLog.objects.all()
    commits = FilterParams(request, commits)
    commits = commits.values('repository__id', 'repository__name', 'author__id', 'author__account', 'author__display')
    commits = commits.annotate(commit_count=Count('id'))
    commits = commits.order_by('-commit_count')[:10]

    return HttpResponse(json.dumps(list(commits)), 'application/json')


