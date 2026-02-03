#!/bin/bash
# ===========================================
# Sentimatrix Studio Setup Script
# ===========================================
# Usage: ./scripts/setup.sh [environment]
# Sets up a new server for Sentimatrix Studio deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT=${1:-development}
DEPLOY_PATH="/opt/sentimatrix"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root or with sudo"
        exit 1
    fi
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."

    if command -v docker &> /dev/null; then
        log_warn "Docker is already installed"
        return
    fi

    # Install Docker using official script
    curl -fsSL https://get.docker.com | sh

    # Add current user to docker group
    usermod -aG docker ${SUDO_USER:-$USER}

    # Start Docker service
    systemctl enable docker
    systemctl start docker

    log_success "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    log_info "Installing Docker Compose..."

    if docker compose version &> /dev/null; then
        log_warn "Docker Compose is already installed"
        return
    fi

    # Docker Compose V2 comes with Docker Engine
    # Install plugin if not available
    DOCKER_CONFIG=${DOCKER_CONFIG:-/usr/local/lib/docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

    log_success "Docker Compose installed successfully"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."

    mkdir -p ${DEPLOY_PATH}/{backups,logs,data}
    mkdir -p ${DEPLOY_PATH}/data/{mongodb,redis}

    # Set permissions
    chown -R ${SUDO_USER:-$USER}:${SUDO_USER:-$USER} ${DEPLOY_PATH}

    log_success "Directories created"
}

# Configure firewall
configure_firewall() {
    log_info "Configuring firewall..."

    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp   # SSH
        ufw allow 80/tcp   # HTTP
        ufw allow 443/tcp  # HTTPS
        ufw --force enable
        log_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        log_success "firewalld configured"
    else
        log_warn "No firewall found, skipping configuration"
    fi
}

# Generate secrets
generate_secrets() {
    log_info "Generating secrets..."

    SECRET_KEY=$(openssl rand -base64 32 | tr -d '=+/' | head -c 32)
    ENCRYPTION_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -base64 32 | tr -d '=+/' | head -c 32)
    MONGO_PASSWORD=$(openssl rand -base64 24 | tr -d '=+/')

    log_success "Secrets generated"

    # Display secrets
    echo ""
    echo "=========================================="
    echo "Generated Secrets (SAVE THESE SECURELY)"
    echo "=========================================="
    echo ""
    echo "SECRET_KEY=${SECRET_KEY}"
    echo "ENCRYPTION_KEY=${ENCRYPTION_KEY}"
    echo "JWT_SECRET_KEY=${JWT_SECRET}"
    echo "MONGO_ROOT_PASSWORD=${MONGO_PASSWORD}"
    echo ""
    echo "=========================================="
    echo ""
}

# Create environment file template
create_env_template() {
    log_info "Creating environment file template..."

    cat > ${DEPLOY_PATH}/.env.template << 'EOF'
# ===========================================
# Sentimatrix Studio Environment Configuration
# ===========================================

# Domain Configuration
DOMAIN=sentimatrix.io
ACME_EMAIL=admin@sentimatrix.io

# Database
MONGODB_URL=mongodb://sentimatrix:${MONGO_ROOT_PASSWORD}@mongodb:27017
DATABASE_NAME=sentimatrix_studio
MONGO_ROOT_USERNAME=sentimatrix
MONGO_ROOT_PASSWORD=CHANGE_ME

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THESE!)
SECRET_KEY=CHANGE_ME_32_CHARS_MIN
ENCRYPTION_KEY=CHANGE_ME_64_HEX_CHARS
JWT_SECRET_KEY=CHANGE_ME_32_CHARS_MIN
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://sentimatrix.io,https://www.sentimatrix.io

# Traefik
TRAEFIK_AUTH=admin:$$apr1$$xyz... # Generate with: htpasswd -nb admin password

# Optional: Error Tracking
SENTRY_DSN=

# Optional: External Services
GROQ_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF

    log_success "Environment template created at ${DEPLOY_PATH}/.env.template"
}

# Install monitoring tools
install_monitoring() {
    log_info "Setting up monitoring..."

    # Create Prometheus config directory
    mkdir -p ${DEPLOY_PATH}/monitoring/prometheus

    # Prometheus configuration
    cat > ${DEPLOY_PATH}/monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics

  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8082']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
EOF

    log_success "Monitoring configuration created"
}

# Set up log rotation
setup_log_rotation() {
    log_info "Setting up log rotation..."

    cat > /etc/logrotate.d/sentimatrix << EOF
${DEPLOY_PATH}/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ${SUDO_USER:-$USER} ${SUDO_USER:-$USER}
    sharedscripts
    postrotate
        docker kill -s USR1 \$(docker ps -q --filter name=sentimatrix) 2>/dev/null || true
    endscript
}
EOF

    log_success "Log rotation configured"
}

# Set up automatic updates
setup_auto_updates() {
    log_info "Setting up automatic security updates..."

    if command -v apt-get &> /dev/null; then
        apt-get install -y unattended-upgrades
        dpkg-reconfigure -plow unattended-upgrades
        log_success "Automatic updates configured (apt)"
    elif command -v dnf &> /dev/null; then
        dnf install -y dnf-automatic
        systemctl enable --now dnf-automatic.timer
        log_success "Automatic updates configured (dnf)"
    fi
}

# Main setup function
main() {
    echo ""
    echo "=========================================="
    echo "  Sentimatrix Studio Server Setup"
    echo "  Environment: ${ENVIRONMENT}"
    echo "=========================================="
    echo ""

    check_root
    install_docker
    install_docker_compose
    create_directories
    configure_firewall
    generate_secrets
    create_env_template
    install_monitoring
    setup_log_rotation
    setup_auto_updates

    echo ""
    log_success "Server setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.template to .env.${ENVIRONMENT} and fill in your values"
    echo "2. Copy your docker-compose.prod.yml to ${DEPLOY_PATH}"
    echo "3. Run: cd ${DEPLOY_PATH} && docker-compose -f docker-compose.prod.yml up -d"
    echo ""
    echo "For more information, see the deployment documentation."
    echo ""
}

main "$@"
