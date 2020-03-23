# -*- coding: utf-8
from .utils import session

DEBUG = True

SECRET_KEY = "ThisIsASecretKeyThatIsOnlyUsedForUnitTestingAndNotForAnyDeployedEnvironments"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

ROOT_URLCONF = "katka.urls"

FIELD_ENCRYPTION_KEY = "OnlyUsedForUnitTestingNotForProdEnvironment="


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.sessions",
    "rest_framework",
    "katka.apps.KatkaCoreConfig",
    "tests.unit",
    "encrypted_model_fields",
]

MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

TEMPLATES = (
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            )
        },
    },
)

TIME_ZONE = "UTC"
USE_TZ = True

REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"

PIPELINE_RUNNER_SESSION = session.Session()
PIPELINE_RUNNER_BASE_URL = None
PIPELINE_CHANGE_NOTIFICATION_EP = None
PIPELINE_UPDATE_STEP_EP = None
