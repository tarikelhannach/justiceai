#!/bin/bash

# restore.sh - Script de Restauración
# Sistema Judicial Digital - Marruecos
# Uso: ./scripts/restore.sh [backup_timestamp] [db|files|logs|full]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$1
RESTORE_TYPE=${2:-full}

# Database configuration
DB_CONTAINER="db"
DB_NAME=${PGDATABASE:-justicia_db}
DB_USER=${PGUSER:-justicia}

# Validation
if [ -z "$TIMESTAMP" ]; then
    echo -e "${RED}❌ Error: Debe especificar un timestamp de backup${NC}"
    echo ""
    echo "Backups disponibles:"
    echo "===================="
    ls -lt $BACKUP_DIR/full/ | grep "full_backup" | head -10
    echo ""
    echo "Uso: ./scripts/restore.sh [TIMESTAMP] [db|files|logs|full]"
    echo "Ejemplo: ./scripts/restore.sh 20241013_140000 full"
    exit 1
fi

echo -e "${BLUE}🔄 Sistema de Restauración - Justicia Digital Marruecos${NC}"
echo "=================================="
echo "Timestamp: $TIMESTAMP"
echo "Tipo: $RESTORE_TYPE"
echo ""

# Functions
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Confirm restoration
confirm_restore() {
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Esta operación sobrescribirá los datos actuales${NC}"
    echo ""
    read -p "¿Está seguro que desea continuar? (escriba 'SI' para confirmar): " confirm
    
    if [ "$confirm" != "SI" ]; then
        echo -e "${RED}Restauración cancelada${NC}"
        exit 0
    fi
}

# Restore Database
restore_database() {
    echo -e "${BLUE}📊 Restaurando base de datos...${NC}"
    
    local backup_file="$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql.gz"
    
    if [ ! -f $backup_file ]; then
        print_error "Backup de base de datos no encontrado: $backup_file"
        exit 1
    fi
    
    # Verify integrity
    if ! gunzip -t $backup_file 2>/dev/null; then
        print_error "Archivo de backup corrupto"
        exit 1
    fi
    
    print_status "Integridad del backup verificada"
    
    # Create backup of current database before restore
    echo -e "${YELLOW}Creando backup de seguridad antes de restaurar...${NC}"
    local safety_backup="$BACKUP_DIR/database/db_pre_restore_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose ps | grep -q $DB_CONTAINER; then
        docker-compose exec -T $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $safety_backup
    else
        PGPASSWORD=$PGPASSWORD pg_dump -h ${PGHOST:-localhost} -U $DB_USER -d $DB_NAME > $safety_backup
    fi
    
    print_status "Backup de seguridad creado: $safety_backup"
    
    # Restore database
    echo -e "${BLUE}Restaurando desde: $backup_file${NC}"
    
    if docker-compose ps | grep -q $DB_CONTAINER; then
        # Drop and recreate database
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "DROP DATABASE IF EXISTS ${DB_NAME}_temp;"
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "CREATE DATABASE ${DB_NAME}_temp;"
        
        # Restore to temp database
        gunzip -c $backup_file | docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -d ${DB_NAME}_temp
        
        # Swap databases
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "ALTER DATABASE $DB_NAME RENAME TO ${DB_NAME}_old;"
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "ALTER DATABASE ${DB_NAME}_temp RENAME TO $DB_NAME;"
        docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -c "DROP DATABASE ${DB_NAME}_old;"
    else
        # Local restore
        gunzip -c $backup_file | PGPASSWORD=$PGPASSWORD psql -h ${PGHOST:-localhost} -U $DB_USER -d $DB_NAME
    fi
    
    print_status "Base de datos restaurada exitosamente"
}

# Restore Files
restore_files() {
    echo -e "${BLUE}📁 Restaurando archivos...${NC}"
    
    local backup_file="$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz"
    
    if [ ! -f $backup_file ]; then
        print_error "Backup de archivos no encontrado: $backup_file"
        exit 1
    fi
    
    # Backup current files
    echo -e "${YELLOW}Creando backup de archivos actuales...${NC}"
    local safety_backup="./uploads_backup_$(date +%Y%m%d_%H%M%S)"
    
    if [ -d "uploads" ]; then
        cp -r uploads $safety_backup
        print_status "Backup de seguridad creado: $safety_backup"
    fi
    
    # Restore files
    tar -xzf $backup_file
    
    print_status "Archivos restaurados exitosamente"
}

# Restore Logs
restore_logs() {
    echo -e "${BLUE}📝 Restaurando logs...${NC}"
    
    local backup_file="$BACKUP_DIR/logs/logs_backup_$TIMESTAMP.tar.gz"
    
    if [ ! -f $backup_file ]; then
        print_error "Backup de logs no encontrado: $backup_file"
        exit 1
    fi
    
    # Restore logs
    tar -xzf $backup_file
    
    print_status "Logs restaurados exitosamente"
}

# Full Restore
restore_full() {
    echo -e "${BLUE}💾 Restauración completa del sistema...${NC}"
    
    local full_backup="$BACKUP_DIR/full/full_backup_$TIMESTAMP.tar.gz"
    
    if [ ! -f $full_backup ]; then
        print_error "Backup completo no encontrado: $full_backup"
        exit 1
    fi
    
    # Extract full backup
    echo -e "${BLUE}Extrayendo backup completo...${NC}"
    tar -xzf $full_backup
    
    # Restore components
    restore_database
    restore_files
    restore_logs
    
    print_status "Sistema restaurado completamente"
}

# Restart services
restart_services() {
    echo -e "${BLUE}🔄 Reiniciando servicios...${NC}"
    
    if docker-compose ps > /dev/null 2>&1; then
        docker-compose restart
        print_status "Servicios reiniciados"
    fi
}

# Verify restoration
verify_restoration() {
    echo -e "${BLUE}🔍 Verificando restauración...${NC}"
    
    # Check database
    if docker-compose ps | grep -q $DB_CONTAINER; then
        local db_tables=$(docker-compose exec -T $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "\dt" | wc -l)
        print_status "Base de datos verificada ($db_tables tablas)"
    fi
    
    # Check files
    if [ -d "uploads" ]; then
        local file_count=$(find uploads -type f | wc -l)
        print_status "Archivos verificados ($file_count archivos)"
    fi
    
    # Check logs
    if [ -d "logs" ]; then
        local log_count=$(find logs -type f | wc -l)
        print_status "Logs verificados ($log_count archivos)"
    fi
}

# Main execution
confirm_restore

case $RESTORE_TYPE in
    "db"|"database")
        restore_database
        ;;
    "files")
        restore_files
        ;;
    "logs")
        restore_logs
        ;;
    "full")
        restore_full
        ;;
    *)
        print_error "Tipo de restauración inválido: $RESTORE_TYPE"
        echo "Uso: ./restore.sh [timestamp] [full|db|files|logs]"
        exit 1
        ;;
esac

# Restart services
restart_services

# Verify restoration
verify_restoration

echo ""
echo -e "${GREEN}✅ Restauración completada exitosamente!${NC}"
echo ""
echo -e "${YELLOW}Recomendaciones post-restauración:${NC}"
echo "1. Verificar logs del sistema"
echo "2. Probar funcionalidad crítica"
echo "3. Verificar integridad de datos"
echo "4. Notificar al equipo sobre la restauración"
echo ""
