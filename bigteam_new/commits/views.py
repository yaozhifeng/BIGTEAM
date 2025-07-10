# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib import messages
import datetime
from .models import Repository, Author, CommitLog, UpdateRepositories


def home(request):
    """Home view showing overview of all projects and team member performance."""
    # Project list with author count
    projects = Repository.objects.values('id', 'name', 'desc', 'vcs_type')
    projects = projects.annotate(author_count=Count('commits__author', distinct=True))
    projects = projects.annotate(commit_count=Count('commits'))

    return render(request, 'home.html', {
        'projects': projects,
    })


def project(request, project_id):
    """Project view showing member performance within a project."""
    project = get_object_or_404(Repository, pk=project_id)

    today = datetime.date.today()
    last_month_day = today - datetime.timedelta(days=30)

    # Participants - authors who have commits in this project
    coders = Author.objects.filter(commits__repository=project)
    coders = coders.annotate(author_commits=Count('commits'))
    coders = coders.order_by('-author_commits')
    
    return render(request, 'project.html', {
        'project': project,
        'coders': coders,
    })


def person(request, person_id):
    """Personal view showing detail of each individual."""
    author = get_object_or_404(Author, pk=person_id)
    
    # Get projects this author has contributed to
    projects = Repository.objects.filter(commits__author=author).distinct()
    projects = projects.annotate(
        commit_count=Count('commits', filter={'commits__author': author})
    )
    
    # Get recent commits by this author
    recent_commits = CommitLog.objects.filter(author=author).order_by('-time')[:20]
    
    return render(request, 'person.html', {
        'coder': author,
        'projects': projects,
        'recent_commits': recent_commits,
    })


def update_all(request):
    """Update all repositories by fetching new commits."""
    try:
        updated_count, failed_count = UpdateRepositories()
        
        if failed_count == 0:
            messages.success(
                request, 
                f'Successfully updated {updated_count} repositories.'
            )
        else:
            messages.warning(
                request,
                f'Updated {updated_count} repositories successfully, '
                f'{failed_count} failed. Check logs for details.'
            )
    except Exception as e:
        messages.error(request, f'Error updating repositories: {e}')

    return redirect('commits:home')
