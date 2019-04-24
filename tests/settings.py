# -*- coding: utf-8
from .utils import session

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't)c0g-tbhgoe2ybv4(iyj%!07*si)co@rg21f&ejm3v=)u^_-8'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'katka.urls'

FIELD_ENCRYPTION_KEY = 'SURdYnt6gHdgq84TgewXS6WayBQYlHt9Lr8Sryv9yOI='

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.sessions',

    'rest_framework',

    'katka.apps.KatkaCoreConfig',

    'tests.unit',

    'encrypted_model_fields'
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATES = (
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            )
        }
    },
)

REQUESTS_CA_BUNDLE = '/etc/ssl/certs/ca-certificates.crt'

PIPELINE_CHANGE_NOTIFICATION_SESSION = session.Session()
PIPELINE_CHANGE_NOTIFICATION_URL = None
