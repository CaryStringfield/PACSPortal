"""
WSGI config for pacs-portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys, site
from os.path import join
from django.core.wsgi import get_wsgi_application



PROJECT_DIR = '/home/pacs-portal_project'

# Add the app's directory to the PYTHONPATH
sys.path.append(PROJECT_DIR)
sys.path.append(join(PROJECT_DIR,'app'))


# Add the site-packages of the chosen virtualenv to work with
site.addsitedir(join(PROJECT_DIR,'env/lib/python2.7/site-packages'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleus.settings")

# Activate your virtual env
activate_env=os.path.expanduser(join(PROJECT_DIR,'env/bin/activate_this.py'))
execfile(activate_env, dict(__file__=activate_env))

import django
django.setup()
application = django.core.handlers.wsgi.WSGIHandler()

from nucleus import auth
