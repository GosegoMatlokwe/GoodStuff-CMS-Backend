"""
WSGI config for backend_cms project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
# Import the standard WSGI application loader from Django
from django.core.wsgi import get_wsgi_application

# Tell Django which settings file to use (backend_cms/settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_cms.settings')

# Create the WSGI application instance that the server will use to communicate with Django
application = get_wsgi_application()