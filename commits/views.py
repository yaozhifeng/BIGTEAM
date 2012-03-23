# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Sum, Count
import datetime
from models import *
from coffin.shortcuts import render_to_response

#home view
def home(request):
    #project list
    projects = Repository.objects.values('id', 'name', 'desc')
    projects = projects.annotate(author_count=Count('commits__author', distinct=True))


    return render_to_response('home.html',
                {
                    'projects': projects,
                },
                context_instance = RequestContext(request)
            )

#project view    
def project(request, project_id):
    project = get_object_or_404(Repository, pk=project_id)

    today = datetime.date.today()
    lastmonth_day = today - datetime.timedelta(days=30)

    #participants
    coders = Author.objects.filter(commits__repository=project)
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')
    
    return render_to_response('project.html',
            {
                'project': project,
                'coders': coders,
            },
            context_instance = RequestContext(request)
        )

def person(request, person_id):
    author = get_object_or_404(Author, pk=person_id)
    
    return render_to_response('person.html',
            {
                'coder': author,
            },
            context_instance = RequestContext(request)
        )

#update all
def update_all(request):
    UpdateRepositories();

    return redirect('home')
