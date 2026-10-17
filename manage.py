#!/usr/bin/env python
# The line above is called a "shebang". It tells Linux/Mac systems to use the python interpreter to run this file.

"""Django's command-line utility for administrative tasks."""
# The line above is just a description (docstring) of what this file does.

import os
# We import the 'os' module so we can interact with the operating system (like reading environment variables).

import sys
# We import the 'sys' module so we can access command-line arguments (like when you type 'python manage.py runserver').

def main():
    """Run administrative tasks."""
    # This sets an environment variable telling Django where to find your project settings.
    # It looks for 'settings.py' inside the 'backend_cms' folder.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_cms.settings')
    
    try:
        # We try to import Django's built-in command-line executor.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # If the import fails, it means Django isn't installed or your virtual environment isn't activated.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # This is the magic line! It takes the arguments you typed in the terminal 
    # (like 'runserver' or 'makemigrations') and executes them.
    execute_from_command_line(sys.argv)

# This checks if the script is being run directly (not imported as a module elsewhere).
if __name__ == '__main__':
    # If it is, it calls the main() function above to start the process.
    main()