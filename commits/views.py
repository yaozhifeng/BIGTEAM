# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db.models import Sum, Count
import datetime
from models import *

#home view
def home(request):
    #project list
    projects = Repository.objects.values('id', 'name', 'desc')
    projects = projects.annotate(author_count=Count('commits__author', distinct=True))

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=30)

    #coder of the month
    coders = Author.objects.all()
    coders = coders.filter(commits__time__range=(lastmonth_day, today))
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')[0:10]

    #recent commits
    commits = CommitLog.objects.values(
            'revision',
            'comment', 
            'time', 
            'repository__name', 
            'author__account', 
            'author__display').order_by('-time')[:10]

    #data for generating the graph
    select_data = {"date": """strftime('%%Y-%%m-%%d', time)"""}
    graph = CommitLog.objects.filter(time__range=(lastmonth_day, today))
    graph = graph.extra(select=select_data).values('date').annotate(commit_count=Count('id'))

    stats = {}
    #generate commit graph for each project
    for project in projects:
        #stats[project['name']] = graph
        g = graph.filter(repository=project['id'])
        line = '['
        for day in g:
            line = line + '["%s", %d],' % (day['date'], day['commit_count'])
        line = line + ']'
 
        stats[project['name']] = line

    #import pdb
    #pdb.set_trace()

    return render_to_response('home.html',
                {
                    'projects': projects,
                    'coders': coders,
                    'commits': commits,
                    'graph': stats,
                },
                context_instance = RequestContext(request)
            )

#project view    
def project(request, project_id):
    project = get_object_or_404(Repository, pk=project_id)

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=30)

    #recent commits
    commits = project.commits.values(
            'revision',
            'comment',
            'time',
            'author__account',
            'author__display').order_by('-time')[:10]

    #participants
    coders = Author.objects.filter(commits__repository=project)
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')
    
    #graph of participants contribution
    #data for generating the graph
    select_data = {"date": """strftime('%%Y-%%m-%%d', time)"""}
    graph = CommitLog.objects.filter(time__range=(lastmonth_day, today)).filter(repository=project)
    graph = graph.extra(select=select_data).values('date').annotate(commit_count=Count('id'))

    stats = {}
    for coder in coders:
        g = graph.filter(author=coder)
        line = '['
        for day in g:
            line = line + '["%s", %d],' % (day['date'], day['commit_count'])
        line = line + ']'

        if line != '[]':
            stats[coder.display if len(coder.display)>0 else coder.account] = line

    return render_to_response('project.html',
            {
                'project': project,
                'commits': commits,
                'coders': coders,
                'graph': stats,
            },
            context_instance = RequestContext(request)
        )

def person(request, person_id):
    #import pdb;
    #pdb.set_trace();
    author = get_object_or_404(Author, pk=person_id)
    
    #recent commits
    commits = CommitLog.objects.filter(author=author)
    commits = commits.values('repository__name', 'time', 'comment')
    commits = commits.order_by('-time')[0:10]

    #personal information
    coder = {}
    coder['account'] = author.account
    coder['display'] = author.display
    coder['commits'] = CommitLog.objects.filter(author__id=person_id).count()
    coder['recent_commits'] = 0

    #participated projects
    projects = Repository.objects.values('id', 'name').filter(commits__author=author).annotate(commits_count=Count('commits'))

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=30)

    #contribution graph for each project
    select_data = {"date": """strftime('%%Y-%%m-%%d', time)"""}
    graph = CommitLog.objects.filter(time__range=(lastmonth_day, today)).filter(author=author)
    graph = graph.extra(select=select_data).values('date').annotate(commit_count=Count('id'))

    stats = {}
    for project in projects:
        g = graph.filter(repository=project['id'])
        line = '['
        for day in g:
            line = line + '["%s", %d],' % (day['date'], day['commit_count'])
        line = line + ']'
 
        stats[project['name']] = line

       

    return render_to_response('person.html',
            {
                'coder': coder,
                'commits': commits,
                'projects': projects,
                'graph': stats,
            },
            context_instance = RequestContext(request)
        )


