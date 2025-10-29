# 🏛️ Digital Judicial System - Kingdom of Morocco

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-Government-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)

**Complete judicial digitization system with government compliance for Morocco**

[Documentation](#documentation) •
[Features](#features) •
[Installation](#installation) •
[Deployment](#deployment) •
[Support](#support)

</div>

---

## 📋 Description

The Digital Judicial System of Morocco is a comprehensive judicial management platform designed to modernize the legal system of the Kingdom of Morocco. The system provides secure case management, document processing with multi-language OCR, advanced semantic search, digital signature with HSM, and full compliance with government regulations.

### 🎯 System Objectives

- ✅ Complete digitization of judicial processes
- ✅ Secure case management with granular RBAC
- ✅ OCR processing in Arabic, French, and Spanish
- ✅ Advanced semantic search with Elasticsearch
- ✅ Digital signature with HSM (Hardware Security Module)
- ✅ Complete audit and government compliance
- ✅ Scalability for government workloads

---

## ✨ Key Features

### 🔐 Security and Authentication

- **JWT Authentication** with access and refresh tokens
- **Rate Limiting** (SlowAPI): protection against brute force and DDoS
- **RBAC** (Role-Based Access Control) with 5 roles: Admin, Judge, Lawyer, Clerk, Citizen
- **Complete Audit Logging** of all system actions
- **HSM Integration** for secure digital signatures
- **Field-level permissions** for granular data control

### 📁 Case Management

- Complete CRUD with RBAC validation
- Advanced multi-criteria search
- Case status with workflow
- Automatic assignment to judges
- Complete change history
- Report export

### 📄 Document Processing

- **Multi-language OCR**: Arabic, French, Spanish (Tesseract)
- Secure upload with type and size validation
- Storage with RBAC access control
- Full-text search in documents
- PDF generation with watermark
- Digital signature with HSM

### 🔍 Semantic Search

- Elasticsearch with full Arabic support
- Multi-field search with relevance
- Advanced filters (date, type, status, etc.)
- Result highlighting
- Auto-complete suggestions

### 📊 Audit Dashboard

- Statistics visualization with Recharts
- Advanced filters (user, action, date, resource)
- Robust pagination with AbortController
- JSON/CSV export
- Admin/clerk access only (RBAC)

### 🌐 Internationalization

- **3 languages**: Spanish, French, Arabic
- **RTL Support**: Automatic Right-to-Left layout for Arabic
- Selected language persistence
- Automatic browser language detection

### 🎨 User Interface

- Material-UI v5 with modern design
- Dark/light theme with persistence
- Signature purple gradient
- Glassmorphism effects
- Responsive for mobile/tablet/desktop
- Role-specific dashboards

---

## 🏗️ System Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Cache**: Redis 7
- **Search**: Elasticsearch 8.11
- **Auth**: python-jose, passlib
- **OCR**: Tesseract (ara+fra+spa)
- **Tasks**: Celery with specialized workers
- **Rate Limiting**: SlowAPI

#### Frontend
- **Framework**: React 18 with Vite
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **i18n**: react-i18next
- **Charts**: Recharts

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Load Balancer**: Nginx
- **Monitoring**: Grafana, Flower, Redis Commander
- **CI/CD**: GitHub Actions (ready)
- **HSM**: PKCS#11, Azure Key Vault, Software Fallback

### Services and Components

```
┌─────────────────────────────────────────────────────┐
│                  Load Balancer (Nginx)              │
│                     Port 80/443                     │
└──────────────────────┬──────────────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
  ┌───▼───┐       ┌───▼───┐       ┌───▼───┐
  │ App 1 │       │ App 2 │       │ App 3 │
  │ :8000 │       │ :8000 │       │ :8000 │
  └───┬───┘       └───┬───┘       └───┬───┘
      │                │                │
      └────────────────┼────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
  ┌───▼────┐     ┌────▼────┐     ┌─────▼──────┐
  │ Postgr │     │  Redis  │     │Elasticsrch │
  │   SQL  │     │ :6379   │     │   :9200    │
  └────────┘     └─────────┘     └────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
  ┌───▼──────┐   ┌────▼─────┐   ┌──────▼─────┐
  │Celery CPU│   │Celery I/O│   │ Celery HSM │
  │ Worker   │   │  Worker  │   │   Worker   │
  └──────────┘   └──────────┘   └────────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.0+
- **Server**: 8GB RAM minimum, 4 CPUs, 100GB storage

### Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital

# 2. Configure environment variables
cp .env.example .env
nano .env  # Edit with production values

# 3. Generate secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy to .env

# 4. Run deployment
./deploy.sh production

# 5. Verify services
docker-compose ps
curl http://localhost/health
```

### Critical Environment Variables

```bash
# Security (MANDATORY to change)
SECRET_KEY="[generate-secure-32-character-key]"
POSTGRES_PASSWORD="[secure-password]"
GRAFANA_ADMIN_PASSWORD="[grafana-password]"

# Database
DATABASE_URL="postgresql://justicia:${POSTGRES_PASSWORD}@db:5432/justicia_db"

# Production domains
ALLOWED_ORIGINS="https://justicia.ma,https://www.justicia.ma"
ALLOWED_HOSTS="justicia.ma,www.justicia.ma"
```

---

## 📚 Documentation

### Available Guides

| Document | Description |
|-----------|-------------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Complete deployment guide with Docker |
| **[TESTING.md](backend/TESTING.md)** | Testing and coverage guide |
| **[CODE_QUALITY.md](backend/CODE_QUALITY.md)** | Code standards and linting |
| **[scripts/README.md](scripts/README.md)** | Backups and recovery |
| **[replit.md](replit.md)** | Architecture and technical decisions |

### Useful Commands

```bash
# Testing
cd backend && ./run_tests.sh all           # All tests
cd backend && ./run_tests.sh coverage      # With coverage

# Code Quality
cd backend && ./format.sh                  # Format (Black + isort)
cd backend && ./lint.sh                    # Lint (Flake8 + mypy)

# Backups
./scripts/backup.sh full                   # Full backup
./scripts/restore.sh 20241013_140000 full  # Restore

# Deployment
./deploy.sh production                     # Deploy production
./deploy.sh health                         # Health check
```

---

## 🔒 Security

### Rate Limiting

- **Login**: 5 attempts/minute per IP (brute force protection)
- **Registration**: 3 attempts/hour per IP (spam prevention)
- **API**: 100 requests/minute per authenticated user

### Audit

- All events logged in PostgreSQL
- Retention: 7 years (2555 days - legal requirement)
- JSON/CSV export for analysis
- Dashboard with visualizations

### HSM - Digital Signature

```bash
# Hardware HSM (PKCS#11)
HSM_TYPE=pkcs11
HSM_LIBRARY_PATH=/usr/lib/hsm/libhsm.so
HSM_PIN=secure-pin

# Azure Key Vault (Cloud HSM)
HSM_TYPE=azure_keyvault
AZURE_KEY_VAULT_URL=https://morocco-kv.vault.azure.net/
```

---

## 👥 Roles and Permissions

| Role | Permissions |
|-----|----------|
| **Admin** | Complete system management, users, configuration |
| **Judge** | Assigned case management, decisions, documents |
| **Lawyer** | View cases, upload documents, communications |
| **Clerk** | Administrative support, case registration, audit |
| **Citizen** | Query own cases, status, public documents |

---

## 🧪 Testing

### Test Coverage

- **Target**: ≥95% coverage
- **Unit Tests**: Isolated modules (auth, cases, documents)
- **Integration Tests**: External services (DB, Redis, ES)
- **Security Tests**: XSS, CSRF, SQL injection, rate limiting
- **API Tests**: All endpoints with RBAC
- **Performance Tests**: Concurrent load (≥1500 users)

### Run Tests

```bash
cd backend

# All tests
./run_tests.sh all

# By category
./run_tests.sh unit
./run_tests.sh security
./run_tests.sh api

# With HTML coverage
./run_tests.sh coverage
open htmlcov/index.html
```

---

## 📊 Monitoring

### Monitoring Services

| Service | Port | URL | Description |
|----------|--------|-----|-------------|
| **Flower** | 5555 | http://server:5555 | Celery monitoring |
| **Redis Commander** | 8081 | http://server:8081 | Redis management |
| **ES Head** | 9100 | http://server:9100 | Elasticsearch monitor |
| **Grafana** | 3000 | http://server:3000 | Dashboards and metrics |

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

## 🔄 Backups and Recovery

### Automated Backups

```bash
# Configure cron
./scripts/setup-cron.sh

# Schedule: Daily at 2 AM (configurable)
BACKUP_SCHEDULE="0 2 * * *"
```

### Backup Procedures

```bash
# Full backup
./scripts/backup.sh full

# Specific backup
./scripts/backup.sh db      # Database only
./scripts/backup.sh files   # Files only
./scripts/backup.sh logs    # Logs only
```

### Restoration

```bash
# List available backups
ls -lth backups/full/

# Restore from timestamp
./scripts/restore.sh 20241013_140000 full
```

**Backup Features:**
- ✅ Automatic gzip compression
- ✅ Complete integrity verification
- ✅ Automatic cleanup (30-day retention)
- ✅ S3 upload (optional)
- ✅ Fail-fast with validation
- ✅ Detailed reports

---

## 🌍 Internationalization

### Supported Languages

| Language | Code | RTL | Status |
|--------|--------|-----|--------|
| Spanish | `es` | No | ✅ Complete |
| French | `fr` | No | ✅ Complete |
| Arabic | `ar` | Yes | ✅ Complete |

### Change Language

```javascript
// In the frontend
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

// Change language
i18n.changeLanguage('ar');  // Arabic
i18n.changeLanguage('fr');  // French
i18n.changeLanguage('es');  // Spanish
```

---

## 🛠️ Local Development

### Development Setup

```bash
# 1. Clone and configure
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital
cp .env.example .env

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt

# 3. Install frontend dependencies
cd ../frontend
npm install

# 4. Start services (PostgreSQL, Redis, ES)
docker-compose up -d db redis elasticsearch

# 5. Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Start frontend
cd frontend
npm run dev
```

### Pre-commit Hooks

```bash
cd backend

# Install hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📞 Support

### Contact

- **Technical Email**: soporte-tecnico@justicia.ma
- **Phone**: +212 537 XXX XXX
- **Documentation**: https://docs.justicia.ma
- **Issues**: https://github.com/morocco-gov/sistema-judicial-digital/issues

### Contribution

This is a government project. Contributions must follow:

1. Fork the repository
2. Branch for feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request with security review

---

## 📄 License

This software is property of the **Kingdom of Morocco - Ministry of Justice**.  
Government use only. Redistribution prohibited without authorization.

---

## 🏆 Production Features

✅ **Security**: JWT, RBAC, Rate Limiting, Audit Logging  
✅ **Scalability**: Horizontal scaling with load balancer  
✅ **Reliability**: Health checks, auto-restart, automated backups  
✅ **Compliance**: Complete audit, legal retention, HSM  
✅ **Performance**: Redis cache, Elasticsearch, Celery workers  
✅ **Monitoring**: Grafana, Flower, structured logs  
✅ **Testing**: ≥95% coverage, security tests, load tests  
✅ **Documentation**: Complete in EN/ES/FR/AR  

---

<div align="center">

**Digital Judicial System - Kingdom of Morocco** 🇲🇦

*Modernizing justice with secure and scalable technology*

**Version 1.0.0** | October 2025

</div>
