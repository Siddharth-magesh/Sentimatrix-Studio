#!/bin/bash
#
# MongoDB Backup Script for Sentimatrix Studio
#
# This script creates backups of the MongoDB database using mongodump.
# Backups are compressed and stored with timestamps.
#
# Usage:
#   ./scripts/backup_db.sh [OPTIONS]
#
# Options:
#   -h, --host       MongoDB host (default: localhost)
#   -p, --port       MongoDB port (default: 27017)
#   -d, --database   Database name (default: sentimatrix_studio)
#   -o, --output     Output directory (default: ./backups)
#   -r, --retention  Days to keep backups (default: 7)
#   --uri            Full MongoDB URI (overrides host/port)
#   --help           Show this help message
#
# Examples:
#   ./scripts/backup_db.sh
#   ./scripts/backup_db.sh --host mongodb --port 27017
#   ./scripts/backup_db.sh --uri "mongodb+srv://user:pass@cluster.mongodb.net"
#   ./scripts/backup_db.sh --retention 30
#

set -e

# Default configuration
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
DATABASE_NAME="${DATABASE_NAME:-sentimatrix_studio}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
MONGO_URI=""

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
    head -35 "$0" | tail -28
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
        -o|--output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --uri)
            MONGO_URI="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if mongodump is installed
if ! command -v mongodump &> /dev/null; then
    log_error "mongodump is not installed. Please install MongoDB Database Tools."
    echo "  Ubuntu/Debian: sudo apt-get install mongodb-database-tools"
    echo "  macOS: brew install mongodb-database-tools"
    echo "  Or download from: https://www.mongodb.com/try/download/database-tools"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp for backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="${DATABASE_NAME}_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

log_info "Starting MongoDB backup..."
log_info "  Database: $DATABASE_NAME"
log_info "  Output: $BACKUP_PATH"

# Build mongodump command
DUMP_CMD="mongodump"

if [ -n "$MONGO_URI" ]; then
    # Use URI if provided
    DUMP_CMD="$DUMP_CMD --uri=\"$MONGO_URI\""
    log_info "  Connection: Using provided URI"
else
    # Use host and port
    DUMP_CMD="$DUMP_CMD --host=$MONGO_HOST --port=$MONGO_PORT"
    log_info "  Host: $MONGO_HOST:$MONGO_PORT"
fi

DUMP_CMD="$DUMP_CMD --db=$DATABASE_NAME --out=$BACKUP_PATH"

# Execute backup
log_info "Running mongodump..."
if eval "$DUMP_CMD"; then
    log_info "Backup created successfully at: $BACKUP_PATH"
else
    log_error "Backup failed!"
    exit 1
fi

# Compress backup
log_info "Compressing backup..."
ARCHIVE_NAME="${BACKUP_NAME}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"

cd "$BACKUP_DIR"
tar -czf "$ARCHIVE_NAME" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"
cd - > /dev/null

log_info "Compressed archive: $ARCHIVE_PATH"

# Calculate backup size
BACKUP_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
log_info "Backup size: $BACKUP_SIZE"

# Cleanup old backups
if [ "$RETENTION_DAYS" -gt 0 ]; then
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    DELETED_COUNT=$(find "$BACKUP_DIR" -name "${DATABASE_NAME}_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
    if [ "$DELETED_COUNT" -gt 0 ]; then
        log_info "Deleted $DELETED_COUNT old backup(s)"
    else
        log_info "No old backups to delete"
    fi
fi

# List recent backups
log_info ""
log_info "Recent backups in $BACKUP_DIR:"
ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 || log_warn "No backups found"

log_info ""
log_info "Backup completed successfully!"
log_info ""
log_info "To restore this backup, run:"
log_info "  tar -xzf $ARCHIVE_PATH -C /tmp"
log_info "  mongorestore --db=$DATABASE_NAME /tmp/$BACKUP_NAME/$DATABASE_NAME"
