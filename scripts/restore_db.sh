#!/bin/bash
#
# MongoDB Restore Script for Sentimatrix Studio
#
# This script restores a MongoDB database from a backup archive.
#
# Usage:
#   ./scripts/restore_db.sh <backup_file> [OPTIONS]
#
# Arguments:
#   backup_file      Path to the backup .tar.gz file
#
# Options:
#   -h, --host       MongoDB host (default: localhost)
#   -p, --port       MongoDB port (default: 27017)
#   -d, --database   Database name (default: sentimatrix_studio)
#   --uri            Full MongoDB URI (overrides host/port)
#   --drop           Drop existing collections before restore
#   --help           Show this help message
#
# Examples:
#   ./scripts/restore_db.sh ./backups/sentimatrix_studio_20240101_120000.tar.gz
#   ./scripts/restore_db.sh backup.tar.gz --drop
#   ./scripts/restore_db.sh backup.tar.gz --uri "mongodb://user:pass@host:27017"
#

set -e

# Default configuration
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
DATABASE_NAME="${DATABASE_NAME:-sentimatrix_studio}"
MONGO_URI=""
DROP_COLLECTIONS=false
BACKUP_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show help
show_help() {
    head -30 "$0" | tail -23
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            MONGO_HOST="$2"
            shift 2
            ;;
        -p|--port)
            MONGO_PORT="$2"
            shift 2
            ;;
        -d|--database)
            DATABASE_NAME="$2"
            shift 2
            ;;
        --uri)
            MONGO_URI="$2"
            shift 2
            ;;
        --drop)
            DROP_COLLECTIONS=true
            shift
            ;;
        --help)
            show_help
            ;;
        -*)
            log_error "Unknown option: $1"
            show_help
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                log_error "Unexpected argument: $1"
                show_help
            fi
            shift
            ;;
    esac
done

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    log_error "Backup file is required."
    echo ""
    show_help
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Check if mongorestore is installed
if ! command -v mongorestore &> /dev/null; then
    log_error "mongorestore is not installed. Please install MongoDB Database Tools."
    echo "  Ubuntu/Debian: sudo apt-get install mongodb-database-tools"
    echo "  macOS: brew install mongodb-database-tools"
    echo "  Or download from: https://www.mongodb.com/try/download/database-tools"
    exit 1
fi

# Create temporary directory for extraction
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

log_info "Starting MongoDB restore..."
log_info "  Backup file: $BACKUP_FILE"
log_info "  Database: $DATABASE_NAME"

# Extract backup
log_info "Extracting backup archive..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory (should be the database folder)
BACKUP_DIR=$(find "$TEMP_DIR" -type d -name "$DATABASE_NAME" | head -1)

if [ -z "$BACKUP_DIR" ]; then
    # Try to find any directory that looks like a MongoDB dump
    BACKUP_DIR=$(find "$TEMP_DIR" -mindepth 2 -maxdepth 2 -type d | head -1)
fi

if [ -z "$BACKUP_DIR" ]; then
    log_error "Could not find database backup in archive"
    log_info "Archive contents:"
    ls -la "$TEMP_DIR"
    exit 1
fi

log_info "Found backup directory: $BACKUP_DIR"

# Build mongorestore command
RESTORE_CMD="mongorestore"

if [ -n "$MONGO_URI" ]; then
    RESTORE_CMD="$RESTORE_CMD --uri=\"$MONGO_URI\""
    log_info "  Connection: Using provided URI"
else
    RESTORE_CMD="$RESTORE_CMD --host=$MONGO_HOST --port=$MONGO_PORT"
    log_info "  Host: $MONGO_HOST:$MONGO_PORT"
fi

RESTORE_CMD="$RESTORE_CMD --db=$DATABASE_NAME"

if [ "$DROP_COLLECTIONS" = true ]; then
    RESTORE_CMD="$RESTORE_CMD --drop"
    log_warn "  Mode: DROP existing collections before restore"
else
    log_info "  Mode: Merge with existing data"
fi

RESTORE_CMD="$RESTORE_CMD $BACKUP_DIR"

# Confirm restore if dropping collections
if [ "$DROP_COLLECTIONS" = true ]; then
    echo ""
    log_warn "WARNING: This will DROP all existing collections in '$DATABASE_NAME'!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Restore cancelled."
        exit 0
    fi
fi

# Execute restore
log_info "Running mongorestore..."
if eval "$RESTORE_CMD"; then
    log_info "Database restored successfully!"
else
    log_error "Restore failed!"
    exit 1
fi

# Show collection stats
log_info ""
log_info "Restore completed. Collections in database:"

if [ -n "$MONGO_URI" ]; then
    mongosh "$MONGO_URI" --eval "db.getCollectionNames().forEach(function(c) { print('  ' + c + ': ' + db[c].countDocuments({}) + ' documents'); })" 2>/dev/null || true
else
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/$DATABASE_NAME" --eval "db.getCollectionNames().forEach(function(c) { print('  ' + c + ': ' + db[c].countDocuments({}) + ' documents'); })" 2>/dev/null || true
fi

log_info ""
log_info "Restore completed successfully!"
