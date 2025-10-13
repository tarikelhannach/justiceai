# 🏛️ Sistema Judicial Digital - Reino de Marruecos

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-Government-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18.2-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)

**Sistema completo de digitalización judicial con compliance gubernamental para Marruecos**

[Documentación](#documentación) •
[Características](#características) •
[Instalación](#instalación) •
[Deployment](#deployment) •
[Soporte](#soporte)

</div>

---

## 📋 Descripción

El Sistema Judicial Digital de Marruecos es una plataforma completa de gestión judicial diseñada para modernizar el sistema legal del Reino de Marruecos. El sistema proporciona gestión segura de casos, procesamiento de documentos con OCR multi-idioma, búsqueda semántica avanzada, firma digital con HSM, y cumplimiento total de regulaciones gubernamentales.

### 🎯 Objetivos del Sistema

- ✅ Digitalización completa de procesos judiciales
- ✅ Gestión segura de casos con RBAC granular
- ✅ Procesamiento OCR en árabe, francés y español
- ✅ Búsqueda semántica avanzada con Elasticsearch
- ✅ Firma digital con HSM (Hardware Security Module)
- ✅ Auditoría completa y compliance gubernamental
- ✅ Escalabilidad para cargas gubernamentales

---

## ✨ Características Principales

### 🔐 Seguridad y Autenticación

- **JWT Authentication** con tokens de acceso y refresh
- **Rate Limiting** (SlowAPI): protección contra brute force y DDoS
- **RBAC** (Role-Based Access Control) con 5 roles: Admin, Judge, Lawyer, Clerk, Citizen
- **Audit Logging** completo de todas las acciones del sistema
- **HSM Integration** para firma digital segura
- **Field-level permissions** para control granular de datos

### 📁 Gestión de Casos

- CRUD completo con validación RBAC
- Búsqueda avanzada multi-criterio
- Estados de caso con workflow
- Asignación automática a jueces
- Historial completo de cambios
- Exportación de reportes

### 📄 Procesamiento de Documentos

- **OCR Multi-idioma**: Árabe, Francés, Español (Tesseract)
- Upload seguro con validación de tipo y tamaño
- Almacenamiento con control de acceso RBAC
- Búsqueda full-text en documentos
- Generación de PDF con watermark
- Firma digital con HSM

### 🔍 Búsqueda Semántica

- Elasticsearch con soporte completo de árabe
- Búsqueda multi-campo con relevancia
- Filtros avanzados (fecha, tipo, estado, etc.)
- Highlighting de resultados
- Sugerencias auto-complete

### 📊 Dashboard de Auditoría

- Visualización de estadísticas con Recharts
- Filtros avanzados (usuario, acción, fecha, recurso)
- Paginación robusta con AbortController
- Exportación JSON/CSV
- Solo acceso admin/clerk (RBAC)

### 🌐 Internacionalización

- **3 idiomas**: Español, Francés, Árabe
- **RTL Support**: Layout automático Right-to-Left para árabe
- Persistencia de idioma seleccionado
- Detección automática de idioma del navegador

### 🎨 Interfaz de Usuario

- Material-UI v5 con diseño moderno
- Tema dark/light con persistencia
- Gradiente púrpura característico
- Efectos glassmorphism
- Responsive para mobile/tablet/desktop
- Dashboards específicos por rol

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

#### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Cache**: Redis 7
- **Search**: Elasticsearch 8.11
- **Auth**: python-jose, passlib
- **OCR**: Tesseract (ara+fra+spa)
- **Tasks**: Celery con workers especializados
- **Rate Limiting**: SlowAPI

#### Frontend
- **Framework**: React 18 con Vite
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

### Servicios y Componentes

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

## 🚀 Instalación

### Requisitos Previos

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.0+
- **Servidor**: 8GB RAM mínimo, 4 CPUs, 100GB storage

### Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con valores de producción

# 3. Generar SECRET_KEY segura
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copiar al .env

# 4. Ejecutar deployment
./deploy.sh production

# 5. Verificar servicios
docker-compose ps
curl http://localhost/health
```

### Variables de Entorno Críticas

```bash
# Seguridad (OBLIGATORIO cambiar)
SECRET_KEY="[generar-key-segura-32-caracteres]"
POSTGRES_PASSWORD="[password-segura]"
GRAFANA_ADMIN_PASSWORD="[password-grafana]"

# Base de datos
DATABASE_URL="postgresql://justicia:${POSTGRES_PASSWORD}@db:5432/justicia_db"

# Dominios de producción
ALLOWED_ORIGINS="https://justicia.ma,https://www.justicia.ma"
ALLOWED_HOSTS="justicia.ma,www.justicia.ma"
```

---

## 📚 Documentación

### Guías Disponibles

| Documento | Descripción |
|-----------|-------------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Guía completa de deployment con Docker |
| **[TESTING.md](backend/TESTING.md)** | Guía de testing y cobertura |
| **[CODE_QUALITY.md](backend/CODE_QUALITY.md)** | Estándares de código y linting |
| **[scripts/README.md](scripts/README.md)** | Backups y recuperación |
| **[replit.md](replit.md)** | Arquitectura y decisiones técnicas |

### Comandos Útiles

```bash
# Testing
cd backend && ./run_tests.sh all           # Todos los tests
cd backend && ./run_tests.sh coverage      # Con cobertura

# Code Quality
cd backend && ./format.sh                  # Format (Black + isort)
cd backend && ./lint.sh                    # Lint (Flake8 + mypy)

# Backups
./scripts/backup.sh full                   # Backup completo
./scripts/restore.sh 20241013_140000 full  # Restaurar

# Deployment
./deploy.sh production                     # Deploy producción
./deploy.sh health                         # Health check
```

---

## 🔒 Seguridad

### Rate Limiting

- **Login**: 5 intentos/minuto por IP (brute force protection)
- **Registro**: 3 intentos/hora por IP (spam prevention)
- **API**: 100 requests/minuto por usuario autenticado

### Auditoría

- Todos los eventos logged en PostgreSQL
- Retención: 7 años (2555 días - requisito legal)
- Exportación JSON/CSV para análisis
- Dashboard con visualizaciones

### HSM - Firma Digital

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

## 👥 Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **Admin** | Gestión completa del sistema, usuarios, configuración |
| **Judge** | Gestión de casos asignados, decisiones, documentos |
| **Lawyer** | Ver casos, upload documentos, comunicaciones |
| **Clerk** | Apoyo administrativo, registro de casos, auditoría |
| **Citizen** | Consulta de casos propios, estado, documentos públicos |

---

## 🧪 Testing

### Cobertura de Tests

- **Target**: ≥95% de cobertura
- **Unit Tests**: Módulos aislados (auth, cases, documents)
- **Integration Tests**: Servicios externos (DB, Redis, ES)
- **Security Tests**: XSS, CSRF, SQL injection, rate limiting
- **API Tests**: Todos los endpoints con RBAC
- **Performance Tests**: Carga concurrente (≥1500 usuarios)

### Ejecutar Tests

```bash
cd backend

# Todos los tests
./run_tests.sh all

# Por categoría
./run_tests.sh unit
./run_tests.sh security
./run_tests.sh api

# Con cobertura HTML
./run_tests.sh coverage
open htmlcov/index.html
```

---

## 📊 Monitoreo

### Servicios de Monitoreo

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Flower** | 5555 | http://servidor:5555 | Monitoreo Celery |
| **Redis Commander** | 8081 | http://servidor:8081 | Gestión Redis |
| **ES Head** | 9100 | http://servidor:9100 | Monitor Elasticsearch |
| **Grafana** | 3000 | http://servidor:3000 | Dashboards y métricas |

### Health Checks

```bash
# API principal
curl https://justicia.ma/health

# Database
docker-compose exec db pg_isready -U justicia

# Redis
docker-compose exec redis redis-cli ping

# Elasticsearch
curl http://localhost:9200/_health
```

---

## 🔄 Backups y Recuperación

### Backups Automáticos

```bash
# Configurar cron
./scripts/setup-cron.sh

# Schedule: Diario a las 2 AM (configurable)
BACKUP_SCHEDULE="0 2 * * *"
```

### Procedimientos de Backup

```bash
# Backup completo
./scripts/backup.sh full

# Backup específico
./scripts/backup.sh db      # Solo base de datos
./scripts/backup.sh files   # Solo archivos
./scripts/backup.sh logs    # Solo logs
```

### Restauración

```bash
# Listar backups disponibles
ls -lth backups/full/

# Restaurar desde timestamp
./scripts/restore.sh 20241013_140000 full
```

**Características de Backups:**
- ✅ Compresión gzip automática
- ✅ Verificación de integridad completa
- ✅ Limpieza automática (retención 30 días)
- ✅ Upload a S3 (opcional)
- ✅ Fail-fast con validación
- ✅ Reportes detallados

---

## 🌍 Internacionalización

### Idiomas Soportados

| Idioma | Código | RTL | Estado |
|--------|--------|-----|--------|
| Español | `es` | No | ✅ Completo |
| Francés | `fr` | No | ✅ Completo |
| Árabe | `ar` | Sí | ✅ Completo |

### Cambiar Idioma

```javascript
// En el frontend
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

// Cambiar idioma
i18n.changeLanguage('ar');  // Árabe
i18n.changeLanguage('fr');  // Francés
i18n.changeLanguage('es');  // Español
```

---

## 🛠️ Desarrollo Local

### Setup Desarrollo

```bash
# 1. Clonar y configurar
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital
cp .env.example .env

# 2. Instalar dependencias backend
cd backend
pip install -r requirements.txt

# 3. Instalar dependencias frontend
cd ../frontend
npm install

# 4. Iniciar servicios (PostgreSQL, Redis, ES)
docker-compose up -d db redis elasticsearch

# 5. Iniciar backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Iniciar frontend
cd frontend
npm run dev
```

### Pre-commit Hooks

```bash
cd backend

# Instalar hooks
pip install pre-commit
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

---

## 📞 Soporte

### Contacto

- **Email Técnico**: soporte-tecnico@justicia.ma
- **Tel**: +212 537 XXX XXX
- **Documentación**: https://docs.justicia.ma
- **Issues**: https://github.com/morocco-gov/sistema-judicial-digital/issues

### Contribución

Este es un proyecto gubernamental. Las contribuciones deben seguir:

1. Fork del repositorio
2. Branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request con revisión de seguridad

---

## 📄 Licencia

Este software es propiedad del **Reino de Marruecos - Ministerio de Justicia**.  
Uso exclusivo gubernamental. Prohibida la redistribución sin autorización.

---

## 🏆 Características de Producción

✅ **Security**: JWT, RBAC, Rate Limiting, Audit Logging  
✅ **Scalability**: Horizontal scaling con load balancer  
✅ **Reliability**: Health checks, auto-restart, backups automáticos  
✅ **Compliance**: Auditoría completa, retención legal, HSM  
✅ **Performance**: Redis cache, Elasticsearch, Celery workers  
✅ **Monitoring**: Grafana, Flower, logs estructurados  
✅ **Testing**: ≥95% coverage, security tests, load tests  
✅ **Documentation**: Completa en ES/FR/AR  

---

<div align="center">

**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦

*Modernizando la justicia con tecnología segura y escalable*

**Versión 1.0.0** | Octubre 2025

</div>
