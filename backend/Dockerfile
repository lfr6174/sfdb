# syntax=docker/dockerfile:1
# Production image for the SFDB Django backend.
# Build context is the backend/ directory (Railway "Root Directory" = backend).

FROM python:3.14-slim

# postgresql-client: lets `psql` work inside the container for the one-off seed
# step and DB debugging (kept from the previous railpack.json config).
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so this layer is cached unless requirements change.
# The base/prod/dev split is preserved: production installs the prod lockfile
# only (prod.txt already includes base via pip-compile).
COPY requirements/ requirements/
RUN pip install -r requirements/prod.txt

# Application source.
COPY . .

EXPOSE 8000

# migrate + collectstatic run at boot because they need runtime env vars / the
# database (injected by Railway), then gunicorn serves. $PORT comes from Railway.
CMD python manage.py migrate --noinput \
    && python manage.py collectstatic --noinput \
    && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60
