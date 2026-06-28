#!/usr/bin/env bash
# Bootstrap PostgreSQL roles and permissions for ASL (TD-12).
# Run AFTER Alembic migrations (tables must exist).
#
# Usage:
#   POSTGRES_USER=asl POSTGRES_DB=asl ./deploy/scripts/init-db.sh

set -euo pipefail

: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=asl}"
: "${POSTGRES_PASSWORD:=asl_dev_password}"
: "${POSTGRES_DB:=asl}"
: "${ASL_APP_PASSWORD:=asl_app_password}"

export PGPASSWORD="${POSTGRES_PASSWORD}"
ESCAPED_APP_PASSWORD="${ASL_APP_PASSWORD//\'/\'\'}"

psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF to_regclass('public.decision_records') IS NULL THEN
    RAISE EXCEPTION 'decision_records does not exist — run alembic upgrade head first';
  END IF;
END
\$\$;

DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'asl_app') THEN
    CREATE ROLE asl_app LOGIN PASSWORD '${ESCAPED_APP_PASSWORD}';
  ELSE
    ALTER ROLE asl_app PASSWORD '${ESCAPED_APP_PASSWORD}';
  END IF;
END
\$\$;

GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO asl_app;
GRANT USAGE ON SCHEMA public TO asl_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO asl_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO asl_app;

REVOKE UPDATE, DELETE ON decision_records FROM asl_app;
GRANT SELECT, INSERT ON decision_records TO asl_app;
GRANT UPDATE (final_outcome) ON decision_records TO asl_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO asl_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO asl_app;
SQL

echo "ASL database roles initialized (asl_app: decision_records INSERT+SELECT + final_outcome UPDATE only)."
