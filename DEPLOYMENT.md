# Guía de Deployment - Sistema Judicial Digital Marruecos

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Deployment con Docker](#deployment-con-docker)
4. [Configuración de Producción](#configuración-de-producción)
5. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Software Necesario

- **Docker**: versión 20.10 o superior
- **Docker Compose**: versión 2.0 o superior
- **Certificados SSL**: Para producción (Let's Encrypt recomendado)
- **Servidor**: Mínimo 8GB RAM, 4 CPUs, 100GB almacenamiento

### Puertos Requeridos

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 80 | HTTP | Redirección a HTTPS |
| 443 | HTTPS | Aplicación principal |
| 5432 | PostgreSQL | Base de datos (interno) |
| 6379 | Redis | Cache (interno) |
| 9200 | Elasticsearch | Búsqueda (interno) |
| 5555 | Flower | Monitoreo Celery |
| 8081 | Redis Commander | Monitoreo Redis |
| 9100 | ES Head | Monitoreo Elasticsearch |
| 3000 | Grafana | Dashboard de métricas |

---

## ⚙️ Configuración Inicial

### 1. Clonar Repositorio

```bash
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital
```

### 2. Configurar Variables de Entorno

```bash
# Copiar ejemplo de configuración
cp .env.example .env

# Editar con valores de producción
nano .env
```

**⚠️ IMPORTANTE:** El archivo `docker-compose.yml` está completamente parametrizado con variables de entorno. **NUNCA** contiene credenciales hardcodeadas. Todas las credenciales deben configurarse en el archivo `.env`.

**Variables CRÍTICAS a cambiar en .env:**

```bash
# Seguridad (OBLIGATORIO cambiar)
SECRET_KEY="[generar-key-segura-32-caracteres-minimo]"
POSTGRES_PASSWORD="[password-segura-base-datos]"

# Base de datos
DATABASE_URL="postgresql://justicia:${POSTGRES_PASSWORD}@db:5432/justicia_db"
POSTGRES_DB=justicia_db
POSTGRES_USER=justicia

# Celery (Cache y Workers)
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"

# Dominios (actualizar con dominio real)
ALLOWED_ORIGINS="https://justicia.ma,https://www.justicia.ma"
ALLOWED_HOSTS="justicia.ma,www.justicia.ma"

# Entorno
ENVIRONMENT=production
DEBUG=false

# HSM (Firma Digital) - Producción
HSM_TYPE="pkcs11"  # o "azure_keyvault" o "software_fallback"
# Para HSM hardware:
# HSM_LIBRARY_PATH="/usr/lib/hsm/libhsm.so"
# HSM_PIN="[hsm-pin-seguro]"
```

### 3. Generar SECRET_KEY Segura

```bash
# Método 1: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Método 2: OpenSSL
openssl rand -base64 32
```

---

## 🐳 Deployment con Docker

### Deployment Development

```bash
# Ejecutar script de deployment
./deploy.sh development

# O manualmente
docker-compose up -d
```

### Deployment Production

```bash
# 1. Verificar configuración
./deploy.sh check

# 2. Generar certificados SSL (si no existen)
./deploy.sh ssl

# 3. Inicializar base de datos
./deploy.sh init-db

# 4. Deploy completo
./deploy.sh production

# O manualmente con docker-compose
docker-compose -f docker-compose.yml up -d
```

### Escalado Horizontal

El sistema incluye 3 instancias de la aplicación (app1, app2, app3) balanceadas por Nginx:

```yaml
# Para agregar más instancias, editar docker-compose.yml
app4:
  build: ./backend
  environment:
    - SERVER_ID=app-4
    # ... (copiar configuración de app1-3)
```

---

## 🔐 Configuración de Producción

### 1. Certificados SSL

#### Opción A: Let's Encrypt (Recomendado)

```bash
# Instalar certbot
apt-get install certbot

# Generar certificados
certbot certonly --standalone -d justicia.ma -d www.justicia.ma

# Copiar certificados
cp /etc/letsencrypt/live/justicia.ma/fullchain.pem ./ssl/justicia.crt
cp /etc/letsencrypt/live/justicia.ma/privkey.pem ./ssl/justicia.key

# Auto-renovación (crontab)
0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

#### Opción B: Certificados Propios

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/justicia.key \
  -out ssl/justicia.crt \
  -subj "/C=MA/ST=Rabat/L=Rabat/O=Gobierno de Marruecos/CN=justicia.ma"
```

### 2. Firewall y Seguridad

```bash
# UFW (Ubuntu/Debian)
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH
ufw enable

# Bloquear puertos internos (PostgreSQL, Redis, etc.)
# Solo accesibles desde red Docker interna
```

### 3. HSM - Firma Digital

#### Opción A: Hardware HSM (PKCS#11)

```bash
# Configurar en .env
HSM_TYPE=pkcs11
HSM_LIBRARY_PATH=/usr/lib/hsm/libhsm.so
HSM_PIN=your-secure-pin
HSM_SLOT_ID=0

# Montar volumen HSM en docker-compose.yml
volumes:
  - /dev/bus/usb:/dev/bus/usb  # Para HSM USB
```

#### Opción B: Azure Key Vault (Cloud HSM)

```bash
# Configurar en .env
HSM_TYPE=azure_keyvault
AZURE_KEY_VAULT_URL=https://morocco-justicia-kv.vault.azure.net/
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### 4. Backups Automáticos

```bash
# Configurar en .env
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 2 AM diario
BACKUP_RETENTION_DAYS=30

# Ejecutar script de backup
./scripts/backup.sh
```

---

## 📊 Monitoreo y Mantenimiento

### Servicios de Monitoreo

| Servicio | URL | Usuario | Password |
|----------|-----|---------|----------|
| Flower (Celery) | http://servidor:5555 | - | - |
| Redis Commander | http://servidor:8081 | - | - |
| Elasticsearch Head | http://servidor:9100 | - | - |
| Grafana | http://servidor:3000 | admin | admin123 |

### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f app1
docker-compose logs -f nginx
docker-compose logs -f celery-cpu

# Estado de servicios
docker-compose ps

# Reiniciar servicio específico
docker-compose restart app1

# Ver salud de servicios
./deploy.sh health

# Estadísticas de recursos
docker stats
```

### Health Checks

```bash
# API principal
curl https://justicia.ma/health

# Base de datos
docker-compose exec db pg_isready -U justicia

# Redis
docker-compose exec redis redis-cli ping

# Elasticsearch
curl http://localhost:9200/_health
```

---

## 🚨 Troubleshooting

### Problema: Aplicación no inicia

```bash
# Ver logs detallados
docker-compose logs app1 --tail=100

# Verificar variables de entorno
docker-compose exec app1 env | grep DATABASE_URL

# Reiniciar contenedor
docker-compose restart app1
```

### Problema: Base de datos no conecta

```bash
# Verificar estado de PostgreSQL
docker-compose exec db pg_isready -U justicia -d justicia_db

# Ver logs de DB
docker-compose logs db --tail=50

# Reiniciar DB
docker-compose restart db
```

### Problema: OCR no funciona (árabe)

```bash
# Verificar idiomas instalados
docker-compose exec app1 tesseract --list-langs

# Debería mostrar: ara, fra, spa
# Si falta, reconstruir imagen
docker-compose build --no-cache app1
```

### Problema: Certificados SSL expirados

```bash
# Renovar Let's Encrypt
certbot renew

# Copiar nuevos certificados
cp /etc/letsencrypt/live/justicia.ma/*.pem ./ssl/

# Reiniciar nginx
docker-compose restart nginx
```

### Problema: Falta espacio en disco

```bash
# Limpiar imágenes no usadas
docker system prune -a

# Limpiar logs antiguos
find ./logs -name "*.log" -mtime +30 -delete

# Limpiar archivos temporales
docker-compose exec app1 find /app/temp -type f -mtime +7 -delete
```

---

## 🔄 Actualización del Sistema

### Actualización de Código

```bash
# 1. Backup antes de actualizar
./scripts/backup.sh

# 2. Pull última versión
git pull origin main

# 3. Reconstruir imágenes
docker-compose build --no-cache

# 4. Reiniciar servicios (sin downtime)
docker-compose up -d --force-recreate --no-deps app1
docker-compose up -d --force-recreate --no-deps app2
docker-compose up -d --force-recreate --no-deps app3
```

### Actualización de Base de Datos

```bash
# 1. Backup de DB
docker-compose exec db pg_dump -U justicia justicia_db > backup.sql

# 2. Ejecutar migraciones
docker-compose exec app1 alembic upgrade head

# 3. Verificar integridad
docker-compose exec app1 python -m app.verify_db
```

---

## 📈 Optimización de Performance

### PostgreSQL

```bash
# Editar postgresql.conf para producción
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
max_connections = 200
```

### Redis

```bash
# Configurar maxmemory adecuada
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Elasticsearch

```bash
# Aumentar heap size para grandes volúmenes
ES_JAVA_OPTS=-Xms2g -Xmx2g
```

---

## 📞 Soporte

Para asistencia técnica:

- **Email**: soporte-tecnico@justicia.ma
- **Tel**: +212 537 XXX XXX
- **Documentación**: https://docs.justicia.ma
- **Issues**: https://github.com/morocco-gov/sistema-judicial-digital/issues

---

## 📝 Checklist de Deployment

- [ ] Servidor con requisitos mínimos configurado
- [ ] Docker y Docker Compose instalados
- [ ] Variables de entorno configuradas (.env)
- [ ] SECRET_KEY generada (mínimo 32 caracteres)
- [ ] Passwords de DB cambiadas
- [ ] Certificados SSL instalados (Let's Encrypt o propios)
- [ ] Firewall configurado (puertos 80, 443, 22)
- [ ] HSM configurado (hardware o cloud)
- [ ] Backups automáticos programados
- [ ] Monitoreo configurado (Grafana, Flower)
- [ ] Health checks verificados
- [ ] Logs funcionando correctamente
- [ ] DNS apuntando a servidor
- [ ] ALLOWED_ORIGINS actualizado con dominio real
- [ ] Pruebas de carga realizadas
- [ ] Documentación entregada al equipo

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦
