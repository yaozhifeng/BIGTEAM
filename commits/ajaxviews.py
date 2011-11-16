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

#ajax view for commits statistics per project
def project_summary(request, project_id, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)

    select_data = {"year": """strftime('%%Y', time)""", "month": """strftime('%%m', time)""", "day": """strftime('%%d', time)"""}
    graph = CommitLog.objects.filter(time__year=year, time__month=month)
    graph = graph.extra(select=select_data).values('year', 'month', 'day').annotate(commit_count=Count('id'))
    graph = graph.filter(repository = project_id)

    #pdb.set_trace()
    
    jsonData = json.dumps(list(graph))

    return HttpResponse(jsonData, 'application/json')

#ajax view for project detail
def project_detail(request, project_id, year, month):
    if not request.is_ajax():
        return HttpResponse(status=400)
    
    select_data = {"year": """strftime('%%Y', time)""", "month": """strftime('%%m', time)""", "day": """strftime('%%d', time)"""}
    graph = CommitLog.objects.filter(time__year=year, time__month=month)
    graph = graph.extra(select=select_data).values('year', 'month', 'day', 'author__account', 'author__display').annotate(commit_count=Count('id'))
    graph = graph.filter(repository = project_id)

    #pdb.set_trace()
    
    jsonData = json.dumps(list(graph))

    return HttpResponse(jsonData, 'application/json')



