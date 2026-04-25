from decouple import config

from .base import *

DEBUG = False

# Explicitly require ALLOWED_HOSTS in production environment variables
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])

# Production CORS setup (Should be set via environment variable)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="", cast=lambda v: [s.strip() for s in v.split(",")] if v else []
)

# Basic Security Settings for Production
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
# SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
