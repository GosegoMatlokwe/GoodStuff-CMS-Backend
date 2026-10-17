"""
ASGI config for backend_cms project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""
import os
# Import the standard ASGI application loader from Django
from django.core.asgi import get_asgi_application

# Tell Django which settings file to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_cms.settings')

# Create the ASGI application instance
application = get_asgi_application()