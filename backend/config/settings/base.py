from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
# SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASES, CORS_ALLOWED_ORIGINS
# will be defined in environment-specific settings files (e.g., dev.py, prod.py)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# Admin URL configuration (Falls back to 'admin/' for local development)
ADMIN_URL = config("ADMIN_URL", default="admin/")

# Application definition

INSTALLED_APPS = [
    "unfold",  # Alternative admin GUI
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",  # DRF
    "django_filters",  # django-filter
    "corsheaders",  # django-cors-headers
    "drf_spectacular",  # API schema generator
    # Local apps
    "apps.core",
    "apps.agent",
    "apps.work",
    "apps.concept",
    "apps.post",
    "apps.commit",
    "axes",  # Brute-force protection
    "unfold.contrib.simple_history",  # Unfold styling for simple_history
    "simple_history",  # Model history tracking
]

SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

MIDDLEWARE = [
    # Custom: CORS middleware must be placed as high as possible
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "csp.middleware.CSPMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Custom User Model
AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 14},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/


LANGUAGE_CODE = "zh-hant"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework global settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        # Upgrade to respect Django's built-in model permissions
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "1000/day",
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"


# API Spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Taiwan sf Concept Database API",
    "DESCRIPTION": "API documentation for the Taiwan sf Concept Database",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# django-unfold configuration

UNFOLD = {
    "SITE_HEADER": "TSFDB管理",
    "SITE_TITLE": "TSFDB管理",
}


# AXES (Brute Force Protection) Settings
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]

# Prevent X-Forwarded-For IP spoofing when deployed behind Railway proxy.
# We must use django-ipware (Axes v8+ delegates IP parsing to it).
AXES_CLIENT_IP_CALLABLE = "axes.helpers.get_client_ip_address"

# django-ipware configuration
IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]
# Railway acts as a single reverse proxy layer.
IPWARE_PROXY_COUNT = 1
