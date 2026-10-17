# Import Path from pathlib to handle file paths easily
from pathlib import Path

# BASE_DIR is the absolute path to your project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# CRITICAL SECURITY: Keep this secret in production!
SECRET_KEY = 'django-insecure-683mus)iqhnhb3spwg@90ukxc=gh%ok0n99%j*3^4o!yzb-yu_'

# DEBUG=True shows detailed error pages. Set to False when deploying!
DEBUG = True

# ALLOWED_HOSTS: Which domains can access your site. 
# Added localhost and PythonAnywhere (since I see it in your list)
ALLOWED_HOSTS = ['gosegomatlokwe.pythonanywhere.com', '127.0.0.1', 'localhost']

# INSTALLED_APPS: All the modules your Django project uses
INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin for the theme to work
    'django.contrib.admin', # The built-in admin panel
    'django.contrib.auth', # Authentication system (Users, Passwords)
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Handles CSS/Images
    'catering',  # Your custom app
    
    # --- CRITICAL FOR ANDROID APP ---
    # 'rest_framework', # (If you decide to use DRF later)
    # 'corsheaders',    # (Recommended to allow the app to talk to Django)
]

# MIDDLEWARE: Security layers that process requests
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # --- ADD THIS IF YOU GET CORS ERRORS ON ANDROID ---
    # 'corsheaders.middleware.CorsMiddleware', 
]

# The root URL configuration file
ROOT_URLCONF = 'backend_cms.urls'

# TEMPLATES: Tells Django where your HTML files are
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Tells Django to look in the 'catering/templates' folder
        'DIRS': [BASE_DIR / 'catering' / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Points to your WSGI file
WSGI_APPLICATION = 'backend_cms.wsgi.application'

# DATABASES: 
# NOTE: You are currently using SQLite. For Azure, you MUST change this to PostgreSQL!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation rules (can be left default)
AUTH_PASSWORD_VALIDATORS = [
    # ... keep existing ...
]

# Language and Timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES: Where CSS and Images are stored
STATIC_URL = '/static/'
# Where 'collectstatic' will put files when you deploy
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Where Django looks for YOUR custom CSS during development
STATICFILES_DIRS = [BASE_DIR / 'catering' / 'static']

# Where to redirect users when they try to access a protected page
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# JAZZMIN SETTINGS (Admin Dashboard Theme)
# BUG FIX: You had this dictionary defined twice. I merged them into one.
JAZZMIN_SETTINGS = {
    "site_title": "GoodStuff Catering Admin",
    "site_header": "GoodStuff Catering",
    "site_brand": "GoodStuff Catering",
    # Pointing to your static logo
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "welcome_sign": "Welcome to the GoodStuff Management Portal",
    "copyright": "GoodStuff Catering Ltd",
    "show_ui_builder": False,
    "show_sidebar": True,
    "navigation_expanded": True,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
}

# JAZZMIN UI TWEAKS (Colors and Buttons)
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-white navbar-light",
    "theme": "default",
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_child_indent": True,
    "brand_colour": "navbar-white",
    "brand_small_text": False,
    "accent": "accent-success",
    "button_classes": {
        "primary": "btn-success",
        "secondary": "btn-outline-secondary",
        "info": "btn-success",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}