import os, sys
sys.path.append('/var/sites/')
sys.path.append('/var/sites/bigteam/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bigteam.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

