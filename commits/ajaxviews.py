# Create Ajax views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Sum, Count
import datetime
from models import *
from django.core import serializers
import json
import pdb

#ajax view for overall summary
def summary(request, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)

    #data for generating the graph
    select_data = {"date": """strftime('%%Y-%%m-%%d', time)"""}
    graph = CommitLog.objects.filter(time__year=year, time__month=month)
    graph = graph.extra(select=select_data).values('date').annotate(commit_count=Count('id'))
    #data = json.dumps(list(graph))
    data = '['
    for day in graph:
        data = data + '["%s", %d],' % (day['date'], day['commit_count'])
    data = data + ']'

    #pdb.set_trace()
    return HttpResponse(json.dumps(data), 'application/json')

#ajax view for daily commits statistics
#project id is optional
def project_summary(request, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = {"year": """strftime('%%Y', time)""", "month": """strftime('%%m', time)""", "day": """strftime('%%d', time)"""}
    graph = CommitLog.objects.filter(time__year=year, time__month=month)
    graph = graph.extra(select=select_data).values('repository__name', 'year', 'month', 'day').annotate(commit_count=Count('id'))

    if request.REQUEST.__contains__('project'):
        graph = graph.filter(repository = request.REQUEST['project'])

    return HttpResponse(json.dumps(list(graph)), 'application/json')

#ajax view for project detail
def project_detail(request, project_id, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)
    
    select_data = {"year": """strftime('%%Y', time)""", "month": """strftime('%%m', time)""", "day": """strftime('%%d', time)"""}
    graph = CommitLog.objects.filter(time__year=year, time__month=month)
    graph = graph.extra(select=select_data).values('year', 'month', 'day', 'author__account', 'author__display', 'author__id').annotate(commit_count=Count('id'))
    graph = graph.filter(repository = project_id)

    #pdb.set_trace()
    
    jsonData = json.dumps(list(graph))

    return HttpResponse(jsonData, 'application/json')

#ajax view for recent commits
#optional GET params: project, author
def commits_detail(request, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = { "day": """strftime('%%Y-%%m-%%d', time)""", "time": """strftime('%%H:%%M', time)"""}
    commits = CommitLog.objects.filter(time__year=year, time__month=month)
    commits = commits.extra(select=select_data)
    commits = commits.values('repository__name', 'author__display', 'author__account', 'author__id', 'day', 'time', 'comment', 'revision');

    if request.REQUEST.__contains__('project'):
        commits = commits.filter(repository=request.REQUEST['project'])
    if request.REQUEST.__contains__('author'):
        commits = commits.filter(author=request.REQUEST['author'])

    commits = commits.order_by('-day', '-time')[:20]

    jsonData = json.dumps(list(commits))

    return HttpResponse(jsonData, 'application/json')

#ajax view for coder contributes
#optional GET params: project, author, month, year
def coder_commits(request):
    if not request.is_ajax():
        return HttpResponse(status=400)

    commits = CommitLog.objects.all()

    if request.REQUEST.__contains__('project'):
        commits = commits.filter(repository=request.REQUEST['project'])

    if request.REQUEST.__contains__('author'):
        commits = commits.filter(author=request.REQUEST['author'])

    if request.REQUEST.__contains__('month'):
        commits = commits.filter(time__month=request.REQUEST['month'])

    if request.REQUEST.__contains__('year'):
        commits = commits.filter(time__year=request.REQUEST['year'])

    commits = commits.values('repository__name', 'author__id', 'author__account', 'author__display')
    commits = commits.annotate(commit_count=Count('id'))
    commits = commits.order_by('-commit_count')

    return HttpResponse(json.dumps(list(commits)), 'application/json')


