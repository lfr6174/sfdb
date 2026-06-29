import dj_database_url
from decouple import Csv, config

from .base import *

DEBUG = False

# WhiteNoise serves the collected static files (Django admin / Unfold / DRF
# assets) directly from Gunicorn, so no separate static host is needed on
# Railway. The middleware must sit immediately after SecurityMiddleware.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

# Compressed, hashed filenames with long-lived caching headers.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Explicitly require ADMIN_URL without a default fallback in production.
# This prevents silent fallbacks to 'admin/' if the env variable is missing.
ADMIN_URL = config("ADMIN_URL")

# Railway injects RAILWAY_PUBLIC_DOMAIN automatically (e.g. myapp.up.railway.app),
# so the service's own domain is trusted without manual entry. The ALLOWED_HOSTS
# env var is optional and only needed for extra hosts such as a custom domain.
RAILWAY_PUBLIC_DOMAIN = config("RAILWAY_PUBLIC_DOMAIN", default="")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# Production CORS setup (Must be explicitly provided)
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_METHODS = ["GET", "OPTIONS"]

# Basic Security Settings for Production
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Railway Reverse Proxy Settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
# CSRF trusted origins follow the same pattern: the Railway domain is added
# automatically (with scheme), the env var only adds extra/custom origins.
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_PUBLIC_DOMAIN}")

# HTTPS / TLS / Cookie hardening
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session hardening
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_AGE = 604800
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# Content Security Policy (via django-csp v4.0)
# Note: 'unsafe-inline' is often required by Django Admin / Unfold UI and DRF Browsable APIs.
# 'unsafe-eval' is required by Unfold's bundled Alpine.js, which evaluates
# directive expressions via new AsyncFunction(); without it the admin UI breaks
# (overlays stay stuck, controls unclickable). This CSP only covers the Django
# backend (admin + API); the public site runs on Vercel with its own stricter CSP.
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'none'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],
    }
}

# LOGGING (Production)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} [{name}:{module}:{lineno}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# Database (Production uses PostgreSQL via DATABASE_URL)
# statement_timeout: DB-level circuit breaker — kills any query exceeding 5s.
# Guards against slow-query DoS that bypasses Cloudflare and DRF throttling.
DATABASES = {
    "default": {
        **dj_database_url.parse(
            config("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        ),
        "OPTIONS": {"options": "-c statement_timeout=5000"},
    }
}

# Disable DRF Browsable API in production (force JSON only) to reduce attack surface
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

# Two-factor authentication (production only)
OTP_ADMIN_HIDE_SENSITIVE_DATA = True  # never expose TOTP secrets or QR codes in admin
TWO_FACTOR_REMEMBER_COOKIE_AGE = 5184000  # 60 days
TWO_FACTOR_REMEMBER_COOKIE_SECURE = True
TWO_FACTOR_REMEMBER_COOKIE_SAMESITE = "Strict"
