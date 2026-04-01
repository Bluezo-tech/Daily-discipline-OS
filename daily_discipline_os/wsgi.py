"""
WSGI config for daily_discipline_os project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_discipline_os.settings')

application = get_wsgi_application()