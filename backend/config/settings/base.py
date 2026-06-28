from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Settings shared by every environment. Values that differ per environment
# (DEBUG, ALLOWED_HOSTS, DATABASES, CORS, ...) live in dev.py / prod.py.
# Deployment checklist: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# Admin URL configuration (Falls back to 'admin/' for local development)
ADMIN_URL = config("ADMIN_URL", default="admin/")

# Application definition

INSTALLED_APPS = [
    # Admin theme: "unfold" MUST come before django.contrib.admin so it can
    # override the admin templates. Order matters here.
    "unfold",
    "unfold.contrib.filters",
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",  # REST API toolkit
    "django_filters",  # query-param filtering for DRF
    "corsheaders",  # cross-origin requests from the frontend
    "drf_spectacular",  # OpenAPI schema generation
    # Local apps (one per bounded context)
    "apps.core",
    "apps.agent",
    "apps.work",
    "apps.concept",
    "apps.post",
    "apps.commit",
    # Third-party that hooks into the apps above; kept last so their signals
    # and admin integrations register after our models are loaded.
    "axes",  # brute-force login protection
    "unfold.contrib.simple_history",  # unfold theming for the history admin
    "simple_history",  # row-level audit trail on models
]

SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

# Order matters: each request flows top -> bottom, each response bottom -> top.
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # must be near the top to set CORS headers early
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # sets request.user
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",  # after auth: records failed logins
    "csp.middleware.CSPMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",  # after auth: tags history rows with request.user
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

# Destination for `collectstatic`. Required in production so WhiteNoise can
# serve the admin/Unfold/DRF assets; harmless in dev (where Django serves them
# from each app's static/ dir via the staticfiles finders).
STATIC_ROOT = BASE_DIR / "staticfiles"


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
# Axes v8+ automatically delegates IP parsing to django-ipware if installed.
AXES_CLIENT_IP_CALLABLE = None

# django-ipware configuration
IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]
# Railway acts as a single reverse proxy layer.
IPWARE_PROXY_COUNT = 1
