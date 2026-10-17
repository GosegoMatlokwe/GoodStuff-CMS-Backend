""" URL configuration for backend_cms project. """
# Import the built-in Django admin module
from django.contrib import admin
# Import path for routing, and include to link to other url files
from django.urls import path, include

# This list defines the routes for your entire project
urlpatterns = [
    # When a user goes to /admin/, send them to the Django admin interface
    path('admin/', admin.site.urls),
    
    # When a user goes to the root URL (/), load the urls.py file from the 'catering' app.
    # This means all your dashboard pages and API endpoints will be handled there.
    path('', include('catering.urls')), 
]