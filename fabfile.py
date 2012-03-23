from fabric.api import *
from fabric.contrib.files import exists

env.hosts = ['chenxia@172.16.16.38']
env.password = 'rdSleCsq'
site_dir = '/var/sites/bigteam'

@task
def migrate():
    with cd(site_dir):
        sudo('python manage.py migrate')

@task
def deploy():
    with cd(site_dir):
        sudo('git pull')
        sudo('touch django.wsgi')

@task
def backup():
    with cd(site_dir):
        if not exists('backup'):
            sudo('mkdir backup')
        if exists('backup/repository.json'):
            sudo('rm backup/repository.json')
        sudo('python manage.py dumpdata commits.repository --indent 4 >> \
                ./backup/repository.json')
        get('backup/repository.json', './backup/repository.json')
        if exists('backup/author.json'):
            sudo('rm backup/author.json')
        sudo('python manage.py dumpdata commits.author --indent 4 >> \
                ./backup/author.json')
        get('backup/author.json', './backup/author.json')

