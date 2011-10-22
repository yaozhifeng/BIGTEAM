# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db.models import Sum, Count
import datetime
from models import *

def home(request):
    projects = Repository.objects.values('name', 'desc')
    projects = projects.annotate(author_count=Count('commits__author', distinct=True))

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=60)

    coders = Author.objects.all()
    #coders = coders.values('commits__time')
    coders = coders.filter(commits__time__range=(lastmonth_day, today))
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')

    commits = CommitLog.objects.values(
            'revision',
            'comment', 
            'time', 
            'repository__name', 
            'author__account', 
            'author__display').order_by('-time')[:10]

    for commit in commits:
        print commit

    return render_to_response('home.html',
                {
                    'projects': projects,
                    'coders': coders,
                    'commits': commits,
                },
                context_instance = RequestContext(request)
                )

