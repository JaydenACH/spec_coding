#!/bin/bash

# Database backup script for PostgreSQL
# This script creates compressed backups with rotation

set -e

# Configuration
DB_HOST="${DB_HOST:-db}"
DB_NAME="${POSTGRES_DB}"
DB_USER="${POSTGRES_USER}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${DATE}.sql.gz"
KEEP_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Backup function
create_backup() {
    log "Starting backup of database ${DB_NAME}"
    
    # Set password for pg_dump
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Create backup
    pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=custom \
        --compress=9 \
        --no-owner \
        --no-privileges \
        | gzip > "${BACKUP_FILE}"
    
    # Check if backup was successful
    if [ $? -eq 0 ]; then
        log "Backup completed successfully: ${BACKUP_FILE}"
        
        # Get backup size
        BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
        log "Backup size: ${BACKUP_SIZE}"
    else
        log "ERROR: Backup failed!"
        exit 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than ${KEEP_DAYS} days"
    
    find "${BACKUP_DIR}" -name "backup_${DB_NAME}_*.sql.gz" -type f -mtime +${KEEP_DAYS} -delete
    
    if [ $? -eq 0 ]; then
        log "Old backups cleaned up successfully"
    else
        log "WARNING: Error cleaning up old backups"
    fi
}

# Health check function
health_check() {
    log "Performing database health check"
    
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Simple connection test
    pg_isready -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}"
    
    if [ $? -eq 0 ]; then
        log "Database health check: OK"
    else
        log "ERROR: Database health check failed!"
        exit 1
    fi
}

# Verify backup function
verify_backup() {
    log "Verifying backup integrity"
    
    # Test if the backup file can be read
    gunzip -t "${BACKUP_FILE}"
    
    if [ $? -eq 0 ]; then
        log "Backup verification: OK"
    else
        log "ERROR: Backup verification failed!"
        exit 1
    fi
}

# Main execution
main() {
    log "=== Database Backup Script Started ==="
    
    # Perform health check first
    health_check
    
    # Create the backup
    create_backup
    
    # Verify the backup
    verify_backup
    
    # Cleanup old backups
    cleanup_old_backups
    
    log "=== Database Backup Script Completed ==="
}

# Run main function
main

# Exit successfully
exit 0 