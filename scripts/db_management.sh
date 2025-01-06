#!/bin/bash

# Create a development database clone
create_db_clone() {
    local SOURCE_DB="internal"
    local DEV_DB="pf_internal_dev"
    
    # Stop connections to source database
    psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$SOURCE_DB';"
    
    # Create new database as a clone
    createdb -T "$SOURCE_DB" "$DEV_DB"
    
    echo "Created development database: $DEV_DB"
}

# Create a database schema snapshot
create_db_snapshot() {
    local DB_NAME=$1
    local SCHEMA_NAME=$2
    local TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    local BACKUP_FILE="personaflow_db_snapshot_${TIMESTAMP}.sql"
    
    # Dump only the specified schema
    pg_dump -d "$DB_NAME" -n "$SCHEMA_NAME" -f "$BACKUP_FILE"
    
    echo "Created database snapshot: $BACKUP_FILE"
}

# Restore database from snapshot
restore_db_snapshot() {
    local DB_NAME=$1
    local BACKUP_FILE=$2
    
    # Restore the database from snapshot
    psql -d "$DB_NAME" -f "$BACKUP_FILE"
    
    echo "Restored database from snapshot: $BACKUP_FILE"
}

# Usage examples:
# ./db_management.sh create_clone
# ./db_management.sh create_snapshot internal personaflow
# ./db_management.sh restore_snapshot internal backup_file.sql