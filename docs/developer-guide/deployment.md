# Deployment Guide

This guide covers deploying Sentimatrix Studio to production environments.

## Prerequisites

- Docker and Docker Compose
- Access to a cloud provider (AWS, GCP, Azure, etc.)
- Domain name with DNS access
- SSL certificate (or use Let's Encrypt)

## Docker Deployment

### Production Docker Compose

Create a production-ready `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - DATABASE_NAME=sentimatrix_studio
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mongodb
      - redis
    networks:
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: arq app.workers.main.WorkerSettings
    restart: always
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongodb
      - redis
    networks:
      - internal
    deploy:
      replicas: 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    restart: always
    networks:
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.frontend.tls=true"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"

  mongodb:
    image: mongo:6
    restart: always
    volumes:
      - mongodb_data:/data/db
    networks:
      - internal
    command: mongod --wiredTigerCacheSizeGB 1

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - internal
    command: redis-server --appendonly yes

  traefik:
    image: traefik:v2.10
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_certs:/letsencrypt
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    networks:
      - internal

volumes:
  mongodb_data:
  redis_data:
  traefik_certs:

networks:
  internal:
```

### Backend Dockerfile

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run with Gunicorn
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile.prod`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build arguments
ARG NEXT_PUBLIC_API_URL

# Build application
COPY . .
RUN npm run build

# Production image
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
```

## Cloud Deployments

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Create ECR repositories:**

```bash
aws ecr create-repository --repository-name sentimatrix-backend
aws ecr create-repository --repository-name sentimatrix-frontend
```

2. **Push images:**

```bash
# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL

# Build and push
docker build -t sentimatrix-backend ./backend
docker tag sentimatrix-backend:latest $ECR_URL/sentimatrix-backend:latest
docker push $ECR_URL/sentimatrix-backend:latest
```

3. **Create ECS task definition** (task-definition.json):

```json
{
  "family": "sentimatrix",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ECR_URL}/sentimatrix-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MONGODB_URL", "value": "mongodb://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "secrets": [
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:ssm:..."}
      ]
    }
  ]
}
```

#### Using AWS App Runner

Simpler deployment for smaller workloads:

```yaml
# apprunner.yaml
version: 1.0
runtime: python311
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
  network:
    port: 8000
```

### GCP Deployment

#### Using Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/sentimatrix-backend ./backend
gcloud run deploy sentimatrix-backend \
  --image gcr.io/$PROJECT_ID/sentimatrix-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/sentimatrix-frontend ./frontend
gcloud run deploy sentimatrix-frontend \
  --image gcr.io/$PROJECT_ID/sentimatrix-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### DigitalOcean Deployment

#### Using App Platform

```yaml
# .do/app.yaml
name: sentimatrix-studio
services:
  - name: backend
    source_dir: /backend
    dockerfile_path: Dockerfile.prod
    http_port: 8000
    routes:
      - path: /api
    envs:
      - key: MONGODB_URL
        scope: RUN_TIME
        value: ${mongodb.DATABASE_URL}
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET

  - name: frontend
    source_dir: /frontend
    dockerfile_path: Dockerfile.prod
    http_port: 3000
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_URL
        scope: BUILD_TIME
        value: ${_self.PUBLIC_URL}/api

databases:
  - name: mongodb
    engine: MONGODB
    production: true
```

## Database Setup

### MongoDB Atlas

For production MongoDB:

1. Create a MongoDB Atlas cluster
2. Configure network access (IP whitelist)
3. Create database user
4. Get connection string

```env
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/sentimatrix_studio?retryWrites=true&w=majority
```

### Redis Cloud

For production Redis:

1. Create Redis Cloud database
2. Enable TLS
3. Get connection details

```env
REDIS_URL=rediss://user:password@redis-host:6379
```

## Environment Variables

### Required Variables

```env
# Database
MONGODB_URL=mongodb://...
DATABASE_NAME=sentimatrix_studio

# Redis
REDIS_URL=redis://...

# Security (generate strong random values)
SECRET_KEY=your-32-char-secret-key
ENCRYPTION_KEY=your-32-byte-encryption-key
JWT_SECRET_KEY=your-jwt-secret-key

# Application
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=https://app.yourdomain.com
```

### Generating Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (must be 32 bytes for AES-256)
python -c "import secrets; print(secrets.token_hex(32))"
```

## SSL/TLS Configuration

### Using Let's Encrypt with Traefik

Included in the docker-compose.prod.yml above.

### Using Cloudflare

1. Add domain to Cloudflare
2. Enable "Full (strict)" SSL mode
3. Create origin certificates
4. Configure in your server

## Monitoring

### Health Checks

The API provides health check endpoints:

```bash
# Liveness check
curl https://api.yourdomain.com/health

# Readiness check (includes DB/Redis)
curl https://api.yourdomain.com/health/ready
```

### Logging

Configure structured logging:

```python
# core/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_obj)
```

### Metrics

Export metrics for Prometheus:

```python
# core/metrics.py
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)
```

## Backup Strategy

### MongoDB Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
mongodump --uri="$MONGODB_URL" --out="/backups/mongodb/$DATE"

# Upload to S3
aws s3 sync /backups/mongodb/$DATE s3://your-backup-bucket/mongodb/$DATE

# Cleanup old backups (keep 30 days)
find /backups/mongodb -type d -mtime +30 -exec rm -rf {} \;
```

### Redis Backup

Redis Cloud and managed services handle this automatically. For self-hosted:

```bash
# Save RDB snapshot
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backups/redis/dump_$(date +%Y%m%d).rdb
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  worker:
    deploy:
      replicas: 5
```

### Load Balancing

Traefik handles load balancing automatically. For AWS:

```yaml
# ALB target group with health checks
TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    HealthCheckPath: /health
    HealthCheckIntervalSeconds: 30
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 5
```

## Rollback Strategy

### Blue-Green Deployment

1. Deploy new version to "green" environment
2. Run smoke tests
3. Switch traffic from "blue" to "green"
4. Keep "blue" running for quick rollback

### Rollback Commands

```bash
# Rollback to previous image
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-build

# Or with specific version
docker-compose -f docker-compose.prod.yml up -d backend:v1.2.3
```

## Security Checklist

- [ ] All secrets in environment variables, not in code
- [ ] HTTPS enforced for all endpoints
- [ ] CORS configured for specific origins
- [ ] Rate limiting enabled
- [ ] Database access restricted by IP
- [ ] Firewall configured for necessary ports only
- [ ] Regular security updates applied
- [ ] Logging and monitoring active
- [ ] Backup strategy tested
- [ ] Incident response plan documented
