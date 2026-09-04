# backend_cms/settings.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-683mus)iqhnhb3spwg@90ukxc=gh%ok0n99%j*3^4o!yzb-yu_'
DEBUG = True
ALLOWED_HOSTS = [ 'gosegomatlokwe.pythonanywhere.com', '127.0.0.1']

INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin for theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catering',  # our app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'catering' / 'templates'],  # added for app templates
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

WSGI_APPLICATION = 'backend_cms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # ... keep existing ...
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'catering' / 'static']  # for custom static files

# Authentication redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Jazzmin settings (optional, but gives dark theme)
JAZZMIN_SETTINGS = {
    "site_title": "Good Stuff Catering Admin",
    "site_header": "Good Stuff Catering",
    "site_brand": "Good Stuff Catering",
    "welcome_sign": "Welcome to the Good Stuff Catering Management System",
    "copyright": "Good Stuff Catering Ltd",
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "dark_mode_theme": "darkly",
}
JAZZMIN_SETTINGS = {
    "site_title": "GoodStuff",
    "site_header": "GoodStuff Catering",
    "site_brand": "GoodStuff",
    "site_logo": "images/logo.png",
    "login_logo": "images/logo.png",
    "welcome_sign": "Welcome to the GoodStuff Management Portal",
    "copyright": "GoodStuff Catering Ltd",
    "show_ui_builder": False,
}

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