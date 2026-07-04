#!/usr/bin/env bash
# Dump Postgres, encrypt with age (public keys only), upload to Cloudflare R2.
# Runs as a Railway cron service: does one backup, then exits.
# Frequency lives in Railway's Cron Schedule setting, not here.
# Retention lives in the R2 lifecycle rule, not here.
#
# DATABASE_URL is passed on pg_dump's command line. In this single-tenant
# container argv and env have the same exposure (everything runs as one user),
# so no URL-parsing is done to hide it; revisit if this ever runs on a shared host.
set -euo pipefail

: "${DATABASE_URL:?}"          # Railway reference -> ${{Postgres.DATABASE_URL}}
: "${AGE_RECIPIENTS:?}"        # space-separated age public keys (age1...);
                               # encrypt to ALL of them so losing one private
                               # key does not orphan the archive
: "${R2_BUCKET:?}"
: "${R2_ENDPOINT:?}"           # https://<account_id>.r2.cloudflarestorage.com
: "${R2_ACCESS_KEY_ID:?}"
: "${R2_SECRET_ACCESS_KEY:?}"
MIN_DUMP_BYTES="${MIN_DUMP_BYTES:-50000}"   # floor for "this dump is not an empty shell"

# rclone reads remote config from env vars (RCLONE_CONFIG_<NAME>_<KEY>), so no
# config file needs to be baked into the image. The remote is named "r2".
export RCLONE_CONFIG_R2_TYPE=s3
export RCLONE_CONFIG_R2_PROVIDER=Cloudflare
export RCLONE_CONFIG_R2_ENDPOINT="$R2_ENDPOINT"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="$R2_ACCESS_KEY_ID"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="$R2_SECRET_ACCESS_KEY"

STAMP="$(date -u +%Y%m%d)"
NAME="tsfdb-${STAMP}.dump.age"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# Each step lands on disk before the next starts (instead of one long pipe to
# the network), so a mid-dump failure aborts the run rather than uploading a
# truncated file that looks like a successful backup.
echo "dumping..."
pg_dump --format=custom --compress=zstd:3 \
        --dbname="$DATABASE_URL" --file="$WORKDIR/db.dump"

# Sanity checks BEFORE encrypting: the TOC must be readable (valid dump
# structure) and the file must not be a near-empty shell, otherwise we would
# upload garbage and report success.
echo "verifying..."
pg_restore --list "$WORKDIR/db.dump" >/dev/null
DUMP_SIZE="$(stat -c%s "$WORKDIR/db.dump")"
if (( DUMP_SIZE < MIN_DUMP_BYTES )); then
  echo "dump is only ${DUMP_SIZE} bytes (< ${MIN_DUMP_BYTES}); refusing to upload" >&2
  exit 1
fi

echo "encrypting..."
read -ra RECIPIENT_KEYS <<< "$AGE_RECIPIENTS"
RECIPIENT_ARGS=()
for key in "${RECIPIENT_KEYS[@]}"; do
  RECIPIENT_ARGS+=(--recipient "$key")
done
age --encrypt "${RECIPIENT_ARGS[@]}" -o "$WORKDIR/$NAME" "$WORKDIR/db.dump"

echo "uploading..."
rclone copyto "$WORKDIR/$NAME" "r2:${R2_BUCKET}/daily/${NAME}"

SIZE="$(stat -c%s "$WORKDIR/$NAME")"
echo "backup ok: ${NAME} (${SIZE} bytes, dump ${DUMP_SIZE} bytes)"

# Dead man's switch: healthchecks.io alerts if this ping stops arriving.
# Optional (skipped when unset) and never allowed to fail the run: the backup
# is already safely in R2 at this point, so a monitoring blip must not make
# Railway record this cron run as failed.
if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
  curl -fsS -m 10 --retry 3 "$HEALTHCHECK_URL" \
       --data-raw "${NAME} ${SIZE} bytes" >/dev/null || true
fi
