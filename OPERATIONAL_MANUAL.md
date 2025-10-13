# Manual Operativo - Sistema Judicial Digital Marruecos

## 📋 Índice

1. [Procedimientos Diarios](#procedimientos-diarios)
2. [Monitoreo del Sistema](#monitoreo-del-sistema)
3. [Gestión de Usuarios](#gestión-de-usuarios)
4. [Backups y Restauración](#backups-y-restauración)
5. [Troubleshooting](#troubleshooting)
6. [Mantenimiento](#mantenimiento)
7. [Escalado y Performance](#escalado-y-performance)
8. [Seguridad y Compliance](#seguridad-y-compliance)

---

## 1. Procedimientos Diarios

### 1.1 Verificación Matutina

Cada mañana, el equipo operativo debe:

```bash
# 1. Verificar estado de servicios
docker-compose ps

# 2. Health check del sistema
curl https://justicia.ma/health

# 3. Verificar métricas clave
docker stats --no-stream

# 4. Revisar logs de errores
docker-compose logs --tail=100 | grep ERROR

# 5. Verificar backup nocturno
ls -lth backups/full/ | head -1
```

**Resultado Esperado:**
- Todos los servicios en estado `Up`
- Health check retorna `{"status": "healthy"}`
- CPU < 70%, Memory < 80%
- Sin errores críticos en logs
- Backup nocturno completado

### 1.2 Revisión de Auditoría

Dashboard: `https://justicia.ma/audit`

1. **Acceder como admin/clerk**
2. **Revisar estadísticas del día anterior:**
   - Total de acciones
   - Usuarios activos
   - Eventos de seguridad
3. **Filtrar por tipo:**
   - LOGIN/LOGOUT: Verificar patrones normales
   - CREATE_CASE: Validar volumen esperado
   - ERROR: Investigar cualquier error
4. **Exportar reporte diario** (JSON/CSV)

### 1.3 Verificación de Backups

```bash
# Verificar último backup
cat backups/backup_report_*.txt | tail -n 1

# Test de integridad
gunzip -t backups/database/db_backup_*.sql.gz
tar -tzf backups/files/files_backup_*.tar.gz > /dev/null
```

---

## 2. Monitoreo del Sistema

### 2.1 Dashboards de Monitoreo

| Dashboard | URL | Credenciales | Propósito |
|-----------|-----|--------------|-----------|
| **Grafana** | http://servidor:3000 | admin / ${GRAFANA_ADMIN_PASSWORD} | Métricas generales |
| **Flower** | http://servidor:5555 | - | Monitoreo Celery |
| **Redis Commander** | http://servidor:8081 | - | Gestión Redis |
| **ES Head** | http://servidor:9100 | - | Monitor Elasticsearch |

### 2.2 Métricas Clave a Monitorear

#### Performance
- **Tiempo de Respuesta**: < 200ms (p95)
- **Throughput**: > 100 req/s
- **Error Rate**: < 1%

#### Recursos
- **CPU**: < 70% promedio
- **Memoria**: < 80% uso
- **Disco**: < 80% uso
- **Network**: < 80% bandwidth

#### Aplicación
- **Usuarios Activos**: Monitorear picos
- **Casos Creados/día**: Baseline establecer
- **Documentos Procesados/hora**: Validar OCR

### 2.3 Alertas Configuradas

```bash
# Verificar alertas en Slack/Email
# Configuradas en .env:
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
ALERT_EMAIL=admin@justicia.ma
```

**Alertas Críticas:**
- CPU > 90% por 5 minutos
- Memoria > 95%
- Disco > 90%
- Error rate > 5%
- Servicio down

---

## 3. Gestión de Usuarios

### 3.1 Crear Usuario

**Frontend:** Dashboard Admin → Usuarios → Crear Usuario

**Backend (CLI):**
```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = User(
    username='nuevo.usuario',
    email='usuario@justicia.ma',
    role='JUDGE',  # ADMIN, JUDGE, LAWYER, CLERK, CITIZEN
    full_name='Nombre Completo'
)
user.set_password('password_temporal')
db.add(user)
db.commit()
print(f'Usuario {user.username} creado')
"
```

### 3.2 Resetear Password

```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'usuario').first()
user.set_password('nueva_password_temporal')
db.commit()
print(f'Password de {user.username} reseteada')
"
```

### 3.3 Cambiar Rol

```bash
docker-compose exec app1 python -c "
from app.models import User, UserRole
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'usuario').first()
user.role = UserRole.ADMIN
db.commit()
print(f'{user.username} ahora es {user.role}')
"
```

### 3.4 Desactivar Usuario

```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'usuario').first()
user.is_active = False
db.commit()
print(f'{user.username} desactivado')
"
```

---

## 4. Backups y Restauración

### 4.1 Backup Manual

```bash
# Backup completo inmediato
./scripts/backup.sh full

# Verificar backup
ls -lth backups/full/ | head -1
cat backups/backup_report_*.txt | tail -n 1
```

### 4.2 Backups Automáticos

**Configurado en cron:**
```bash
# Ver cron jobs
crontab -l

# Resultado esperado:
0 2 * * * cd /ruta/proyecto && ./scripts/backup.sh full >> logs/backup.log 2>&1
```

**Cambiar schedule:**
```bash
export BACKUP_SCHEDULE="0 3 * * *"  # 3 AM
./scripts/setup-cron.sh
```

### 4.3 Restauración

**⚠️ PROCEDIMIENTO CRÍTICO - REQUIERE CONFIRMACIÓN**

```bash
# 1. Listar backups disponibles
ls -lth backups/full/

# 2. Verificar integridad del backup
gunzip -t backups/database/db_backup_20241013_140000.sql.gz
tar -tzf backups/full/full_backup_20241013_140000.tar.gz

# 3. Ejecutar restauración (REQUIERE CONFIRMACIÓN MANUAL)
./scripts/restore.sh 20241013_140000 full

# El script pedirá confirmación:
# ¿Está seguro que desea continuar? (escriba 'SI' para confirmar):
```

### 4.4 Procedimiento de Recuperación ante Desastres

**Escenario: Pérdida total del servidor**

```bash
# 1. Provisionar nuevo servidor (8GB RAM, 4 CPUs)
# 2. Instalar Docker + Docker Compose

# 3. Clonar repositorio
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital

# 4. Copiar backups desde ubicación segura
scp -r backup-server:/backups/* ./backups/

# 5. Configurar .env
cp .env.example .env
nano .env  # Configurar con valores de producción

# 6. Iniciar servicios
docker-compose up -d

# 7. Restaurar desde último backup
./scripts/restore.sh [TIMESTAMP_MAS_RECIENTE] full

# 8. Verificar sistema
curl http://localhost/health
docker-compose ps

# 9. Actualizar DNS si cambió IP
# 10. Verificar SSL/certificados

# RTO (Recovery Time Objective): < 1 hora
# RPO (Recovery Point Objective): < 1 día
```

---

## 5. Troubleshooting

### 5.1 Aplicación No Responde

```bash
# 1. Verificar estado de contenedores
docker-compose ps

# 2. Ver logs recientes
docker-compose logs --tail=100 app1

# 3. Verificar conectividad a DB
docker-compose exec app1 python -c "
from app.database import engine
try:
    engine.connect()
    print('DB OK')
except Exception as e:
    print(f'DB Error: {e}')
"

# 4. Reiniciar aplicación
docker-compose restart app1 app2 app3

# 5. Verificar health check
curl http://localhost/health
```

### 5.2 Base de Datos Lenta

```bash
# 1. Ver conexiones activas
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT count(*) as connections 
    FROM pg_stat_activity 
    WHERE state = 'active';
"

# 2. Ver queries lentas
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
    FROM pg_stat_activity 
    WHERE state = 'active' 
    ORDER BY duration DESC;
"

# 3. Terminar query problemática
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT pg_terminate_backend([PID]);
"

# 4. Vacuum base de datos
docker-compose exec db psql -U justicia -d justicia_db -c "VACUUM ANALYZE;"
```

### 5.3 Redis Out of Memory

```bash
# 1. Ver uso de memoria
docker-compose exec redis redis-cli INFO memory

# 2. Limpiar keys expiradas
docker-compose exec redis redis-cli FLUSHDB

# 3. Aumentar maxmemory (temporal)
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb

# 4. Reiniciar Redis
docker-compose restart redis
```

### 5.4 Celery Workers No Procesan Tareas

```bash
# 1. Ver estado de workers
docker-compose logs celery-cpu --tail=50
docker-compose logs celery-io --tail=50

# 2. Ver cola de tareas
docker-compose exec redis redis-cli LLEN celery

# 3. Purgar cola (CUIDADO)
docker-compose exec app1 celery -A backend.app.celery.celery purge

# 4. Reiniciar workers
docker-compose restart celery-cpu celery-io celery-hsm
```

### 5.5 OCR No Funciona

```bash
# 1. Verificar Tesseract instalado
docker-compose exec app1 tesseract --version

# 2. Verificar idiomas
docker-compose exec app1 tesseract --list-langs

# Debe mostrar: ara, fra, spa

# 3. Si falta idioma, reconstruir imagen
docker-compose build --no-cache app1
docker-compose up -d app1
```

---

## 6. Mantenimiento

### 6.1 Mantenimiento Semanal

**Cada Domingo a las 3 AM:**

```bash
# 1. Backup completo
./scripts/backup.sh full

# 2. Vacuum base de datos
docker-compose exec db psql -U justicia -d justicia_db -c "VACUUM FULL ANALYZE;"

# 3. Limpiar logs antiguos (>30 días)
find ./logs -name "*.log" -mtime +30 -delete

# 4. Limpiar archivos temp
docker-compose exec app1 find /app/temp -type f -mtime +7 -delete

# 5. Limpiar imágenes Docker no usadas
docker system prune -a -f

# 6. Actualizar índice Elasticsearch
curl -X POST "http://localhost:9200/_forcemerge?max_num_segments=1"
```

### 6.2 Mantenimiento Mensual

**Primer domingo de cada mes:**

```bash
# 1. Revisar y rotar logs de audit (>90 días)
docker-compose exec db psql -U justicia -d justicia_db -c "
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
"

# 2. Actualizar certificados SSL (si expiran)
certbot renew

# 3. Revisar y actualizar dependencias de seguridad
cd backend
pip list --outdated
# Actualizar solo patches de seguridad

# 4. Backup offsite (subir a S3/Azure)
aws s3 sync ./backups s3://justicia-backups/$(date +%Y%m)/
```

### 6.3 Actualizaciones del Sistema

```bash
# 1. Backup antes de actualizar
./scripts/backup.sh full

# 2. Pull última versión
git pull origin main

# 3. Reconstruir imágenes
docker-compose build --no-cache

# 4. Actualización sin downtime (rolling update)
docker-compose up -d --force-recreate --no-deps app1
sleep 30
docker-compose up -d --force-recreate --no-deps app2
sleep 30
docker-compose up -d --force-recreate --no-deps app3

# 5. Verificar sistema
curl http://localhost/health
docker-compose logs --tail=100 | grep ERROR

# 6. Si hay problemas, rollback
./scripts/restore.sh [TIMESTAMP_BACKUP] full
```

---

## 7. Escalado y Performance

### 7.1 Escalado Horizontal (Añadir Instancias)

**Editar docker-compose.yml:**

```yaml
  app4:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - SERVER_ID=app-4
      # ... (copiar configuración de app1-3)
```

**Actualizar Nginx (nginx.conf):**

```nginx
upstream backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
    server app4:8000;  # Añadir nueva instancia
}
```

**Aplicar cambios:**

```bash
docker-compose up -d app4
docker-compose restart nginx
```

### 7.2 Optimización de Performance

**PostgreSQL:**

```bash
# Aumentar shared_buffers
docker-compose exec db psql -U justicia -d justicia_db -c "
    ALTER SYSTEM SET shared_buffers = '2GB';
    ALTER SYSTEM SET effective_cache_size = '6GB';
    SELECT pg_reload_conf();
"
```

**Redis:**

```bash
# Aumentar maxmemory
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
```

**Elasticsearch:**

```bash
# Aumentar heap size (editar docker-compose.yml)
ES_JAVA_OPTS=-Xms2g -Xmx2g
```

---

## 8. Seguridad y Compliance

### 8.1 Auditoría de Seguridad

**Mensual:**

```bash
# 1. Revisar intentos de login fallidos
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT user_id, count(*) as attempts 
    FROM audit_logs 
    WHERE action = 'LOGIN' 
      AND details LIKE '%failed%' 
      AND created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id 
    HAVING count(*) > 10;
"

# 2. Revisar cambios de permisos
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT * FROM audit_logs 
    WHERE action IN ('UPDATE_USER', 'CHANGE_ROLE') 
      AND created_at > NOW() - INTERVAL '30 days'
    ORDER BY created_at DESC;
"

# 3. Exportar reporte de auditoría
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=csv&start_date=2024-10-01" \
     > audit_report_$(date +%Y%m).csv
```

### 8.2 Compliance Checklist

**Mensual - Verificar:**

- [ ] Backups completados y verificados (30 días retención)
- [ ] Logs de auditoría intactos (2555 días retención legal)
- [ ] Certificados SSL válidos (>30 días vigencia)
- [ ] Rate limiting activo y funcional
- [ ] HSM funcional (verificar firma digital)
- [ ] Usuarios inactivos desactivados (>90 días sin login)
- [ ] Passwords caducados actualizados (>90 días)
- [ ] Vulnerabilidades de seguridad parcheadas
- [ ] Documentación actualizada
- [ ] Tests de recuperación realizados

---

## 9. Contactos de Emergencia

### Equipo Técnico

| Rol | Nombre | Tel | Email |
|-----|--------|-----|-------|
| **Lead DevOps** | - | +212 XXX XXX XXX | devops@justicia.ma |
| **DBA** | - | +212 XXX XXX XXX | dba@justicia.ma |
| **Security Officer** | - | +212 XXX XXX XXX | security@justicia.ma |
| **On-Call 24/7** | - | +212 XXX XXX XXX | oncall@justicia.ma |

### Proveedores

| Servicio | Contacto | Tel | SLA |
|----------|----------|-----|-----|
| **Hosting** | - | - | 4h response |
| **HSM** | - | - | 2h response |
| **SSL** | - | - | 24h response |

---

## 10. Anexos

### A. Comandos Rápidos

```bash
# Health check completo
./deploy.sh health

# Ver todos los logs
docker-compose logs -f

# Estadísticas de recursos
docker stats

# Conectar a DB
docker-compose exec db psql -U justicia -d justicia_db

# Conectar a Redis
docker-compose exec redis redis-cli

# Ver workers Celery
docker-compose exec app1 celery -A backend.app.celery.celery inspect active
```

### B. Procedimientos de Emergencia

**Sistema completamente caído:**

1. Verificar servidor físico/VM
2. Verificar red/conectividad
3. Reiniciar Docker: `systemctl restart docker`
4. Iniciar servicios: `docker-compose up -d`
5. Verificar logs: `docker-compose logs`
6. Si persiste: Restaurar desde backup

**Incidente de seguridad:**

1. Aislar sistema afectado
2. Notificar Security Officer
3. Capturar evidencia (logs, dumps)
4. Análisis forense
5. Remediar vulnerabilidad
6. Restaurar desde backup limpio
7. Reportar a autoridades (si aplica)

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦
