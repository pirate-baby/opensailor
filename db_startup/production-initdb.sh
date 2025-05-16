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
    # Make postgres user a member of the new user's role
    psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -v ON_ERROR_STOP=1 <<-EOSQL
        GRANT $user TO $POSTGRES_USER;
EOSQL
    psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -v ON_ERROR_STOP=1 <<-EOSQL
        SELECT 'CREATE DATABASE $db OWNER $user'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
}

create_user_and_db "$APP_DB_USER" "$APP_DB_PASSWORD" "$APP_DB"
create_user_and_db "langfuse" "$LANGFUSE_DB_PASSWORD" "langfuse"