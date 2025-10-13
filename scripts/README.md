# Scripts de Backup y Recuperación

## 📋 Descripción

Sistema completo de backup y recuperación para el Sistema Judicial Digital de Marruecos. Incluye backups automáticos programados, restauración granular, y procedimientos de recuperación ante desastres.

## 🔧 Scripts Disponibles

### 1. `backup.sh` - Backup del Sistema

Crea backups de la base de datos, archivos, y logs.

**Uso:**
```bash
./scripts/backup.sh [tipo]
```

**Tipos de backup:**
- `full` - Backup completo (base de datos + archivos + logs)
- `db` - Solo base de datos
- `files` - Solo archivos (uploads, documentos)
- `logs` - Solo logs del sistema

**Ejemplos:**
```bash
# Backup completo
./scripts/backup.sh full

# Solo base de datos
./scripts/backup.sh db

# Solo archivos
./scripts/backup.sh files
```

**Características:**
- ✅ Compresión automática (gzip)
- ✅ Verificación de integridad
- ✅ Limpieza de backups antiguos (configurable)
- ✅ Upload a S3 (opcional)
- ✅ Reporte detallado

### 2. `restore.sh` - Restauración del Sistema

Restaura el sistema desde un backup existente.

**Uso:**
```bash
./scripts/restore.sh [timestamp] [tipo]
```

**Parámetros:**
- `timestamp` - Timestamp del backup (formato: YYYYMMDD_HHMMSS)
- `tipo` - Tipo de restauración: full, db, files, logs

**Ejemplos:**
```bash
# Listar backups disponibles
ls -lt backups/full/

# Restauración completa
./scripts/restore.sh 20241013_140000 full

# Solo restaurar base de datos
./scripts/restore.sh 20241013_140000 db
```

**Características:**
- ✅ Confirmación de seguridad antes de restaurar
- ✅ Backup de seguridad automático pre-restauración
- ✅ Verificación de integridad
- ✅ Reinicio automático de servicios
- ✅ Verificación post-restauración

### 3. `setup-cron.sh` - Configurar Backups Automáticos

Configura cron para ejecutar backups automáticos.

**Uso:**
```bash
./scripts/setup-cron.sh
```

**Schedule por defecto:** Diario a las 2 AM

**Personalizar schedule:**
```bash
# Configurar para ejecutar a las 3 AM
export BACKUP_SCHEDULE="0 3 * * *"
./scripts/setup-cron.sh

# Dos veces al día (2 AM y 2 PM)
export BACKUP_SCHEDULE="0 2,14 * * *"
./scripts/setup-cron.sh
```

**Formatos de cron:**
```
# Formato: minuto hora día mes día_semana
0 2 * * *        # Diario a las 2 AM
0 */6 * * *      # Cada 6 horas
0 2 * * 0        # Cada domingo a las 2 AM
30 1 1 * *       # El 1 de cada mes a la 1:30 AM
```

## 📁 Estructura de Backups

```
backups/
├── database/           # Backups de PostgreSQL
│   ├── db_backup_20241013_140000.sql.gz
│   └── db_backup_20241013_150000.sql.gz
├── files/             # Backups de archivos
│   ├── files_backup_20241013_140000.tar.gz
│   └── files_backup_20241013_150000.tar.gz
├── logs/              # Backups de logs
│   ├── logs_backup_20241013_140000.tar.gz
│   └── logs_backup_20241013_150000.tar.gz
└── full/              # Backups completos
    ├── full_backup_20241013_140000.tar.gz
    └── backup_report_20241013_140000.txt
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Retención de backups (días)
export BACKUP_RETENTION_DAYS=30

# Upload a AWS S3 (opcional)
export AWS_S3_BUCKET=justicia-backups
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Schedule de backups automáticos
export BACKUP_SCHEDULE="0 2 * * *"  # Diario 2 AM
```

### En `.env` o `.env.production`:

```bash
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
AWS_S3_BUCKET=justicia-backups
```

## 🚀 Procedimiento de Recuperación ante Desastres

### Escenario 1: Pérdida Total del Sistema

```bash
# 1. Restaurar código del repositorio
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital

# 2. Copiar backups al servidor
scp -r backups/ usuario@nuevo-servidor:/ruta/proyecto/

# 3. Configurar ambiente
cp .env.example .env
# Editar .env con configuración correcta

# 4. Iniciar servicios
docker-compose up -d

# 5. Restaurar desde backup más reciente
./scripts/restore.sh 20241013_140000 full

# 6. Verificar sistema
docker-compose ps
curl http://localhost/health
```

### Escenario 2: Corrupción de Base de Datos

```bash
# 1. Detener aplicación (mantener DB corriendo)
docker-compose stop app1 app2 app3

# 2. Crear backup de emergencia
docker-compose exec db pg_dump -U justicia justicia_db > emergency_backup.sql

# 3. Restaurar desde último backup bueno
./scripts/restore.sh 20241013_140000 db

# 4. Verificar integridad
docker-compose exec db psql -U justicia -d justicia_db -c "SELECT count(*) FROM cases;"

# 5. Reiniciar aplicación
docker-compose start app1 app2 app3
```

### Escenario 3: Pérdida de Archivos

```bash
# Restaurar solo archivos (uploads, documentos)
./scripts/restore.sh 20241013_140000 files

# Verificar
ls -lh uploads/
```

## 📊 Monitoreo de Backups

### Verificar Logs de Backups

```bash
# Ver logs en tiempo real
tail -f logs/backup.log

# Ver últimos backups
ls -lth backups/full/ | head

# Verificar tamaño de backups
du -sh backups/*
```

### Verificar Cron Jobs

```bash
# Listar cron jobs
crontab -l

# Ver logs de cron (sistema)
grep CRON /var/log/syslog

# Ver resultado último backup
cat backups/backup_report_*.txt | tail -n 1
```

## 🔒 Seguridad de Backups

### Encriptar Backups (Opcional)

```bash
# Encriptar backup con GPG
gpg --symmetric --cipher-algo AES256 backups/full/full_backup_20241013_140000.tar.gz

# Desencriptar
gpg --decrypt backups/full/full_backup_20241013_140000.tar.gz.gpg > backup.tar.gz
```

### Almacenamiento Seguro

1. **Offsite Backups**: Almacenar copias en ubicación física diferente
2. **Cloud Storage**: AWS S3, Azure Blob, Google Cloud Storage
3. **Encriptación**: Usar GPG o similar para datos sensibles
4. **Acceso Restringido**: Permisos estrictos en directorio backups/

```bash
# Restringir permisos
chmod 700 backups/
chmod 600 backups/**/*.gz
```

## 🧪 Testing de Backups

### Test de Backup

```bash
# 1. Crear backup de prueba
./scripts/backup.sh full

# 2. Verificar integridad
gunzip -t backups/database/db_backup_*.sql.gz
tar -tzf backups/files/files_backup_*.tar.gz > /dev/null

# 3. Verificar tamaño
du -sh backups/full/full_backup_*.tar.gz
```

### Test de Restauración (Ambiente de Testing)

```bash
# 1. Crear backup actual
./scripts/backup.sh full

# 2. Hacer cambio de prueba en DB
docker-compose exec db psql -U justicia -d justicia_db -c "INSERT INTO test_table VALUES (999, 'test');"

# 3. Restaurar backup anterior
./scripts/restore.sh [timestamp_anterior] db

# 4. Verificar que cambio de prueba desapareció
docker-compose exec db psql -U justicia -d justicia_db -c "SELECT * FROM test_table WHERE id = 999;"
```

## 📅 Best Practices

### Frecuencia Recomendada

| Tipo | Frecuencia | Retención |
|------|------------|-----------|
| **Base de Datos** | Cada 6 horas | 30 días |
| **Archivos** | Diario | 60 días |
| **Logs** | Diario | 90 días |
| **Backup Completo** | Diario (2 AM) | 30 días |
| **Backup Semanal** | Domingo 3 AM | 180 días |
| **Backup Mensual** | Día 1 del mes | 2 años |

### Checklist de Backup

- [ ] Backups automáticos configurados (cron)
- [ ] Retención de backups configurada (30+ días)
- [ ] Verificación de integridad automática
- [ ] Almacenamiento offsite configurado (S3)
- [ ] Encriptación de backups sensibles
- [ ] Procedimiento de restauración documentado
- [ ] Pruebas de restauración mensuales
- [ ] Monitoreo de espacio en disco
- [ ] Alertas configuradas (fallas de backup)
- [ ] Equipo entrenado en procedimientos

## 🆘 Soporte

Para problemas con backups:

1. **Verificar logs**: `tail -f logs/backup.log`
2. **Verificar espacio**: `df -h`
3. **Verificar permisos**: `ls -la backups/`
4. **Contactar soporte técnico**: soporte-tecnico@justicia.ma

---

**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦  
**Versión**: 1.0.0
