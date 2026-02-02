# Deployment Tasks

## Overview

Deployment and DevOps tasks for Sentimatrix Studio.

---

## Phase 1: Local Development

### 1.1 Docker Setup [P0]

- [ ] Create backend Dockerfile (dev)
- [ ] Create frontend Dockerfile (dev)
- [ ] Create docker-compose.yml (dev)
- [ ] Test local Docker deployment
- [ ] Document local setup

### 1.2 Development Tools [P0]

- [ ] Hot reload for backend
- [ ] Hot reload for frontend
- [ ] Volume mounts for code
- [ ] Environment file templates

---

## Phase 2: CI/CD

### 2.1 GitHub Actions [P0]

- [ ] Create lint workflow
- [ ] Create test workflow (backend)
- [ ] Create test workflow (frontend)
- [ ] Create build workflow
- [ ] Configure branch protection

### 2.2 Quality Gates [P0]

- [ ] Lint check (ruff, ESLint)
- [ ] Type check (mypy, TypeScript)
- [ ] Unit tests pass
- [ ] Coverage thresholds
- [ ] Security scan (bandit, npm audit)

### 2.3 Build Pipeline [P1]

- [ ] Backend Docker image build
- [ ] Frontend Docker image build
- [ ] Push to container registry
- [ ] Tag versioning strategy

---

## Phase 3: Staging

### 3.1 Infrastructure [P1]

- [ ] Set up staging environment
- [ ] Configure staging database
- [ ] Configure staging domain
- [ ] SSL certificate (staging)

### 3.2 Deployment [P1]

- [ ] Staging deploy workflow
- [ ] Smoke tests after deploy
- [ ] Rollback procedure

---

## Phase 4: Production

### 4.1 Infrastructure [P1]

- [ ] Production server setup
- [ ] Load balancer configuration
- [ ] Database setup (MongoDB Atlas / self-hosted)
- [ ] Redis setup (if needed)
- [ ] SSL certificates

### 4.2 Docker Production [P0]

- [ ] Create backend Dockerfile (prod)
- [ ] Create frontend Dockerfile (prod)
- [ ] Create docker-compose.prod.yml
- [ ] Nginx configuration
- [ ] Environment variable management

### 4.3 Deployment Strategy [P1]

- [ ] Blue-green deployment
- [ ] Rolling updates
- [ ] Health check configuration
- [ ] Automated rollback

---

## Phase 5: Monitoring

### 5.1 Logging [P0]

- [ ] Structured logging format
- [ ] Log aggregation setup
- [ ] Log retention policy

### 5.2 Metrics [P1]

- [ ] Application metrics
- [ ] Infrastructure metrics
- [ ] Custom dashboards

### 5.3 Alerting [P1]

- [ ] Error rate alerts
- [ ] Latency alerts
- [ ] Resource usage alerts
- [ ] Downtime alerts

### 5.4 Error Tracking [P1]

- [ ] Sentry integration (backend)
- [ ] Sentry integration (frontend)
- [ ] Error grouping
- [ ] Alert configuration

---

## Phase 6: Security

### 6.1 Secrets Management [P0]

- [ ] Environment variable encryption
- [ ] Secrets rotation procedure
- [ ] API key management

### 6.2 Network Security [P0]

- [ ] Firewall rules
- [ ] VPC configuration (if cloud)
- [ ] IP whitelisting for database

### 6.3 SSL/TLS [P0]

- [ ] Certificate provisioning
- [ ] Auto-renewal (Let's Encrypt)
- [ ] HSTS configuration

### 6.4 Security Scanning [P1]

- [ ] Dependency vulnerability scanning
- [ ] Container image scanning
- [ ] Periodic security audits

---

## Phase 7: Backup

### 7.1 Database Backup [P0]

- [ ] Automated backup schedule
- [ ] Backup retention policy
- [ ] Backup verification
- [ ] Restore procedure documentation

### 7.2 Disaster Recovery [P1]

- [ ] Recovery point objective (RPO)
- [ ] Recovery time objective (RTO)
- [ ] DR procedure documentation
- [ ] DR drill schedule

---

## CI/CD Workflows

### ci.yml

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Backend lint
        run: |
          cd backend
          pip install ruff mypy
          ruff check .
          mypy app
      - name: Frontend lint
        run: |
          cd frontend
          npm ci
          npm run lint
          npm run typecheck

  test-backend:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:6.0
        ports:
          - 27017:27017
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd backend
          pip install -e ".[dev]"
          pytest --cov=app

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd frontend
          npm ci
          npm test -- --coverage

  build:
    needs: [lint, test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: |
          docker build -t sentimatrix-studio-backend ./backend
          docker build -t sentimatrix-studio-frontend ./frontend
```

### deploy.yml

```yaml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push images
        run: |
          docker build -t ${{ secrets.REGISTRY }}/backend:${{ github.ref_name }} ./backend
          docker build -t ${{ secrets.REGISTRY }}/frontend:${{ github.ref_name }} ./frontend
          docker push ${{ secrets.REGISTRY }}/backend:${{ github.ref_name }}
          docker push ${{ secrets.REGISTRY }}/frontend:${{ github.ref_name }}

      - name: Deploy to production
        run: |
          ssh ${{ secrets.DEPLOY_HOST }} "cd /app && ./deploy.sh ${{ github.ref_name }}"
```

---

## Checklist

### Pre-Launch

- [ ] All tests passing
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Backup tested
- [ ] Rollback procedure tested
- [ ] Load testing complete
- [ ] SSL certificates valid
- [ ] DNS configured
- [ ] Environment variables set

### Post-Launch

- [ ] Verify all services running
- [ ] Check error rates
- [ ] Monitor performance
- [ ] Test critical flows
- [ ] Enable alerting
