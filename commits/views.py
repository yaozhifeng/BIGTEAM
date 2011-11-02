# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Sum, Count
import datetime
from models import *

def home(request):
    projects = Repository.objects.values('id', 'name', 'desc')
    projects = projects.annotate(author_count=Count('commits__author', distinct=True))

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=60)

    coders = Author.objects.all()
    #coders = coders.values('commits__time')
    coders = coders.filter(commits__time__range=(lastmonth_day, today))
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')[0:10]

    commits = CommitLog.objects.values(
            'revision',
            'comment', 
            'time', 
            'repository__name', 
            'author__account', 
            'author__display').order_by('-time')[:10]

    return render_to_response('home.html',
                {
                    'projects': projects,
                    'coders': coders,
                    'commits': commits,
                },
                context_instance = RequestContext(request)
            )

def project(request, project_id):
    project = get_object_or_404(Repository, pk=project_id)
    commits = project.commits.values(
            'revision',
            'comment',
            'time',
            'author__account',
            'author__display').order_by('-time')[:10]

    coders = Author.objects.filter(commits__repository=project)
    coders = coders.annotate(author_commits=Count('commits'))
    
    return render_to_response('project.html',
            {
                'project': project,
                'commits': commits,
                'coders': coders,
            },
            context_instance = RequestContext(request)
        )
