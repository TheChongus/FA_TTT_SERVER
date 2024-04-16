# celery.py or tasks.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

#Set the defaul Django settings module for celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tictactoe_server.settings')

#Create a celery app object
app = Celery('tictactoe_server')

#Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

#Auto-discover all tasks.py modules in all Django apps
app.autodiscover_tasks()