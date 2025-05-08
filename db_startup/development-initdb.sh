#!/bin/bash
set -e
export PGPASSWORD=${POSTGRES_PASSWORD}
create_user_and_db() {
    local user=$1
    local password=$2
    local db=$3

    psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -v ON_ERROR_STOP=1 <<-EOSQL
        DO
        \$do\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$user') THEN
                CREATE USER $user WITH PASSWORD '$password';
            END IF;
        END
        \$do\$;
EOSQL
    psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -v ON_ERROR_STOP=1 <<-EOSQL
        SELECT 'CREATE DATABASE $db'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
    psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -v ON_ERROR_STOP=1 <<-EOSQL
        GRANT ALL PRIVILEGES ON DATABASE $db TO $user;
EOSQL
}

create_user_and_db "app" "$APP_DB_PASSWORD" "app"
create_user_and_db "langfuse" "$LANGFUSE_DB_PASSWORD" "langfuse"

if [ "$ENVIRONMENT" = "development" ]; then
    create_user_and_db "app" "$APP_DB_PASSWORD" "test"
fi