# syntax=docker/dockerfile:1
# Standalone Railway cron service: pg_dump -> age encrypt -> upload to R2.
# Build context is the backup/ directory (Railway "Root Directory" = backup).
#
# Base image pins the pg_dump major version, which must be >= the Railway
# Postgres server version (currently postgres-ssl:18).

FROM postgres:18-alpine

# bash: the backup script uses pipefail / [[ ]], which busybox sh lacks.
# age: encryption. rclone: R2 upload. curl: healthcheck ping.
RUN apk add --no-cache bash age rclone curl

COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

# The postgres image ships an unprivileged "postgres" user; no reason to run as root.
USER postgres

ENTRYPOINT ["/usr/local/bin/backup.sh"]
