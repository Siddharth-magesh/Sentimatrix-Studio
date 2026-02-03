#!/bin/bash
# ===========================================
# Sentimatrix Studio Deployment Script
# ===========================================
# Usage: ./scripts/deploy.sh [environment]
# Environments: staging, production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-staging}
DEPLOY_PATH="/opt/sentimatrix"
COMPOSE_FILE="docker-compose.prod.yml"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    if [ ! -f ".env.${ENVIRONMENT}" ]; then
        log_error "Environment file .env.${ENVIRONMENT} not found"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Load environment variables
load_environment() {
    log_info "Loading environment: ${ENVIRONMENT}"

    # Export environment variables from file
    set -a
    source ".env.${ENVIRONMENT}"
    set +a

    export ENVIRONMENT
    log_success "Environment loaded"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."

    docker-compose -f ${COMPOSE_FILE} pull

    log_success "Images pulled successfully"
}

# Backup database
backup_database() {
    log_info "Creating database backup..."

    BACKUP_DIR="${DEPLOY_PATH}/backups"
    BACKUP_FILE="${BACKUP_DIR}/mongodb_$(date +%Y%m%d_%H%M%S).gz"

    mkdir -p ${BACKUP_DIR}

    # Create MongoDB dump
    docker-compose -f ${COMPOSE_FILE} exec -T mongodb mongodump \
        --archive \
        --gzip \
        --db ${DATABASE_NAME:-sentimatrix_studio} \
        > ${BACKUP_FILE} 2>/dev/null || true

    if [ -f "${BACKUP_FILE}" ] && [ -s "${BACKUP_FILE}" ]; then
        log_success "Database backup created: ${BACKUP_FILE}"
    else
        log_warn "Database backup skipped (container may not be running)"
    fi

    # Clean up old backups (keep last 7)
    ls -t ${BACKUP_DIR}/mongodb_*.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."

    # Stop old containers gracefully
    docker-compose -f ${COMPOSE_FILE} stop || true

    # Start services
    docker-compose -f ${COMPOSE_FILE} up -d --remove-orphans

    log_success "Services deployed"
}

# Blue-green deployment for zero downtime
deploy_blue_green() {
    log_info "Performing blue-green deployment..."

    # Scale up new instances
    docker-compose -f ${COMPOSE_FILE} up -d --scale backend=4 --scale frontend=4 --no-recreate

    # Wait for health checks
    log_info "Waiting for new containers to be healthy..."
    sleep 30

    # Check health
    if ! curl -sf http://localhost:8000/health > /dev/null; then
        log_error "Health check failed, rolling back..."
        docker-compose -f ${COMPOSE_FILE} up -d --scale backend=2 --scale frontend=2
        exit 1
    fi

    # Scale down to normal
    docker-compose -f ${COMPOSE_FILE} up -d --scale backend=2 --scale frontend=2 --remove-orphans

    log_success "Blue-green deployment completed"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    docker-compose -f ${COMPOSE_FILE} exec -T backend python -m alembic upgrade head || true

    log_success "Migrations completed"
}

# Health check
health_check() {
    log_info "Running health checks..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:8000/health > /dev/null; then
            log_success "Backend health check passed"
            break
        fi
        log_info "Attempt $attempt/$max_attempts - waiting for backend..."
        sleep 2
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        log_error "Backend health check failed after $max_attempts attempts"
        exit 1
    fi

    # Check frontend
    if curl -sf http://localhost:3000 > /dev/null; then
        log_success "Frontend health check passed"
    else
        log_warn "Frontend health check failed"
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up..."

    # Remove unused Docker resources
    docker system prune -f --filter "until=24h"

    # Remove old images
    docker image prune -af --filter "until=24h"

    log_success "Cleanup completed"
}

# Show status
show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose -f ${COMPOSE_FILE} ps
    echo ""

    log_info "Container logs (last 10 lines):"
    docker-compose -f ${COMPOSE_FILE} logs --tail=10
}

# Rollback deployment
rollback() {
    log_warn "Rolling back to previous deployment..."

    # Get previous image tags
    docker-compose -f ${COMPOSE_FILE} pull --quiet || true

    # Restart with previous images
    docker-compose -f ${COMPOSE_FILE} up -d --force-recreate

    log_success "Rollback completed"
}

# Main deployment function
main() {
    echo ""
    echo "=========================================="
    echo "  Sentimatrix Studio Deployment"
    echo "  Environment: ${ENVIRONMENT}"
    echo "=========================================="
    echo ""

    check_prerequisites
    load_environment

    # Production deployment with zero-downtime
    if [ "${ENVIRONMENT}" = "production" ]; then
        backup_database
        pull_images
        deploy_blue_green
        run_migrations
    else
        # Staging deployment (simpler)
        pull_images
        deploy_services
        run_migrations
    fi

    health_check
    cleanup
    show_status

    echo ""
    log_success "Deployment completed successfully!"
    echo ""
}

# Handle script arguments
case "${2:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        load_environment
        rollback
        ;;
    status)
        show_status
        ;;
    health)
        health_check
        ;;
    backup)
        load_environment
        backup_database
        ;;
    *)
        echo "Usage: $0 [environment] [command]"
        echo ""
        echo "Environments:"
        echo "  staging     Deploy to staging environment (default)"
        echo "  production  Deploy to production environment"
        echo ""
        echo "Commands:"
        echo "  deploy      Full deployment (default)"
        echo "  rollback    Rollback to previous version"
        echo "  status      Show deployment status"
        echo "  health      Run health checks"
        echo "  backup      Create database backup"
        exit 1
        ;;
esac
