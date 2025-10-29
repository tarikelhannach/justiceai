# Deployment Guide - Digital Judicial System Morocco

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Configuration](#initial-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Production Configuration](#production-configuration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software

- **Docker**: version 20.10 or higher
- **Docker Compose**: version 2.0 or higher
- **SSL Certificates**: For production (Let's Encrypt recommended)
- **Server**: Minimum 8GB RAM, 4 CPUs, 100GB storage

### Required Ports

| Port | Service | Description |
|--------|----------|-------------|
| 80 | HTTP | Redirect to HTTPS |
| 443 | HTTPS | Main application |
| 5432 | PostgreSQL | Database (internal) |
| 6379 | Redis | Cache (internal) |
| 9200 | Elasticsearch | Search (internal) |
| 5555 | Flower | Celery monitoring |
| 8081 | Redis Commander | Redis monitoring |
| 9100 | ES Head | Elasticsearch monitoring |
| 3000 | Grafana | Metrics dashboard |

---

## ⚙️ Initial Configuration

### 1. Clone Repository

```bash
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital
```

### 2. Configure Environment Variables

```bash
# Copy configuration example
cp .env.example .env

# Edit with production values
nano .env
```

**⚠️ IMPORTANT:** The `docker-compose.yml` file is fully parameterized with environment variables. It **NEVER** contains hardcoded credentials. All credentials must be configured in the `.env` file.

**CRITICAL variables to change in .env:**

```bash
# Security (MANDATORY to change)
SECRET_KEY="[generate-secure-32-character-minimum-key]"
POSTGRES_PASSWORD="[secure-database-password]"

# Database
DATABASE_URL="postgresql://justicia:${POSTGRES_PASSWORD}@db:5432/justicia_db"
POSTGRES_DB=justicia_db
POSTGRES_USER=justicia

# Celery (Cache and Workers)
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"

# Domains (update with real domain)
ALLOWED_ORIGINS="https://justicia.ma,https://www.justicia.ma"
ALLOWED_HOSTS="justicia.ma,www.justicia.ma"

# Environment
ENVIRONMENT=production
DEBUG=false

# HSM (Digital Signature) - Production
HSM_TYPE="pkcs11"  # or "azure_keyvault" or "software_fallback"
# For hardware HSM:
# HSM_LIBRARY_PATH="/usr/lib/hsm/libhsm.so"
# HSM_PIN="[secure-hsm-pin]"
```

### 3. Generate Secure SECRET_KEY

```bash
# Method 1: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32
```

---

## 🐳 Docker Deployment

### Development Deployment

```bash
# Run deployment script
./deploy.sh development

# Or manually
docker-compose up -d
```

### Production Deployment

```bash
# 1. Verify configuration
./deploy.sh check

# 2. Generate SSL certificates (if they don't exist)
./deploy.sh ssl

# 3. Initialize database
./deploy.sh init-db

# 4. Complete deployment
./deploy.sh production

# Or manually with docker-compose
docker-compose -f docker-compose.yml up -d
```

### Horizontal Scaling

The system includes 3 application instances (app1, app2, app3) balanced by Nginx:

```yaml
# To add more instances, edit docker-compose.yml
app4:
  build: ./backend
  environment:
    - SERVER_ID=app-4
    # ... (copy configuration from app1-3)
```

---

## 🔐 Production Configuration

### 1. SSL Certificates

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
apt-get install certbot

# Generate certificates
certbot certonly --standalone -d justicia.ma -d www.justicia.ma

# Copy certificates
cp /etc/letsencrypt/live/justicia.ma/fullchain.pem ./ssl/justicia.crt
cp /etc/letsencrypt/live/justicia.ma/privkey.pem ./ssl/justicia.key

# Auto-renewal (crontab)
0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

#### Option B: Self-signed Certificates

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/justicia.key \
  -out ssl/justicia.crt \
  -subj "/C=MA/ST=Rabat/L=Rabat/O=Government of Morocco/CN=justicia.ma"
```

### 2. Firewall and Security

```bash
# UFW (Ubuntu/Debian)
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH
ufw enable

# Block internal ports (PostgreSQL, Redis, etc.)
# Only accessible from Docker internal network
```

### 3. HSM - Digital Signature

#### Option A: Hardware HSM (PKCS#11)

```bash
# Configure in .env
HSM_TYPE=pkcs11
HSM_LIBRARY_PATH=/usr/lib/hsm/libhsm.so
HSM_PIN=your-secure-pin
HSM_SLOT_ID=0

# Mount HSM volume in docker-compose.yml
volumes:
  - /dev/bus/usb:/dev/bus/usb  # For USB HSM
```

#### Option B: Azure Key Vault (Cloud HSM)

```bash
# Configure in .env
HSM_TYPE=azure_keyvault
AZURE_KEY_VAULT_URL=https://morocco-justicia-kv.vault.azure.net/
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 4. Automated Backups

```bash
# Configure in .env
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30

# Run backup script
./scripts/backup.sh
```

---

## 📊 Monitoring and Maintenance

### Monitoring Services

| Service | URL | User | Password |
|----------|-----|---------|----------|
| Flower (Celery) | http://server:5555 | - | - |
| Redis Commander | http://server:8081 | - | - |
| Elasticsearch Head | http://server:9100 | - | - |
| Grafana | http://server:3000 | admin | admin123 |

### Useful Commands

```bash
# View logs
docker-compose logs -f app1
docker-compose logs -f nginx
docker-compose logs -f celery-cpu

# Service status
docker-compose ps

# Restart specific service
docker-compose restart app1

# View service health
./deploy.sh health

# Resource statistics
docker stats
```

### Health Checks

```bash
# Main API
curl https://justicia.ma/health

# Database
docker-compose exec db pg_isready -U justicia

# Redis
docker-compose exec redis redis-cli ping

# Elasticsearch
curl http://localhost:9200/_health
```

---

## 🚨 Troubleshooting

### Problem: Application won't start

```bash
# View detailed logs
docker-compose logs app1 --tail=100

# Verify environment variables
docker-compose exec app1 env | grep DATABASE_URL

# Restart container
docker-compose restart app1
```

### Problem: Database won't connect

```bash
# Verify PostgreSQL status
docker-compose exec db pg_isready -U justicia -d justicia_db

# View DB logs
docker-compose logs db --tail=50

# Restart DB
docker-compose restart db
```

### Problem: OCR doesn't work (Arabic)

```bash
# Verify installed languages
docker-compose exec app1 tesseract --list-langs

# Should display: ara, fra, spa
# If missing, rebuild image
docker-compose build --no-cache app1
```

### Problem: SSL certificates expired

```bash
# Renew Let's Encrypt
certbot renew

# Copy new certificates
cp /etc/letsencrypt/live/justicia.ma/*.pem ./ssl/

# Restart nginx
docker-compose restart nginx
```

### Problem: Out of disk space

```bash
# Clean unused images
docker system prune -a

# Clean old logs
find ./logs -name "*.log" -mtime +30 -delete

# Clean temporary files
docker-compose exec app1 find /app/temp -type f -mtime +7 -delete
```

---

## 🔄 System Update

### Code Update

```bash
# 1. Backup before updating
./scripts/backup.sh

# 2. Pull latest version
git pull origin main

# 3. Rebuild images
docker-compose build --no-cache

# 4. Restart services (without downtime)
docker-compose up -d --force-recreate --no-deps app1
docker-compose up -d --force-recreate --no-deps app2
docker-compose up -d --force-recreate --no-deps app3
```

### Database Update

```bash
# 1. DB backup
docker-compose exec db pg_dump -U justicia justicia_db > backup.sql

# 2. Run migrations
docker-compose exec app1 alembic upgrade head

# 3. Verify integrity
docker-compose exec app1 python -m app.verify_db
```

---

## 📈 Performance Optimization

### PostgreSQL

```bash
# Edit postgresql.conf for production
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
max_connections = 200
```

### Redis

```bash
# Configure appropriate maxmemory
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Elasticsearch

```bash
# Increase heap size for large volumes
ES_JAVA_OPTS=-Xms2g -Xmx2g
```

---

## 📞 Support

For technical assistance:

- **Email**: soporte-tecnico@justicia.ma
- **Phone**: +212 537 XXX XXX
- **Documentation**: https://docs.justicia.ma
- **Issues**: https://github.com/morocco-gov/sistema-judicial-digital/issues

---

## 📝 Deployment Checklist

- [ ] Server with minimum requirements configured
- [ ] Docker and Docker Compose installed
- [ ] Environment variables configured (.env)
- [ ] SECRET_KEY generated (minimum 32 characters)
- [ ] DB passwords changed
- [ ] SSL certificates installed (Let's Encrypt or self-signed)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] HSM configured (hardware or cloud)
- [ ] Automated backups scheduled
- [ ] Monitoring configured (Grafana, Flower)
- [ ] Health checks verified
- [ ] Logs working correctly
- [ ] DNS pointing to server
- [ ] ALLOWED_ORIGINS updated with real domain
- [ ] Load tests performed
- [ ] Documentation delivered to team

---

**Version**: 1.0.0  
**Last updated**: October 2025  
**Digital Judicial System - Kingdom of Morocco** 🇲🇦
