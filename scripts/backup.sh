#!/bin/bash

# backup.sh - Script de Backup Automático
# Sistema Judicial Digital - Marruecos
# Uso: ./scripts/backup.sh [full|db|files|logs]

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
BACKUP_TYPE=${1:-full}

# Database configuration
DB_CONTAINER="db"
DB_NAME=${PGDATABASE:-justicia_db}
DB_USER=${PGUSER:-justicia}

echo -e "${BLUE}🔄 Sistema de Backup - Justicia Digital Marruecos${NC}"
echo "=================================="
echo "Tipo: $BACKUP_TYPE"
echo "Timestamp: $TIMESTAMP"
echo "Retención: $RETENTION_DAYS días"
echo ""

# Create backup directory structure
mkdir -p $BACKUP_DIR/{database,files,logs,full}

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

# Backup Database
backup_database() {
    echo -e "${BLUE}📊 Respaldando base de datos...${NC}"
    
    local backup_file="$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql"
    local backup_file_gz="$backup_file.gz"
    
    # Check if running in Docker
    if docker-compose ps | grep -q $DB_CONTAINER; then
        # Docker environment
        docker-compose exec -T $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $backup_file
    else
        # Local PostgreSQL
        PGPASSWORD=$PGPASSWORD pg_dump -h ${PGHOST:-localhost} -U $DB_USER -d $DB_NAME > $backup_file
    fi
    
    if [ $? -eq 0 ]; then
        # Compress backup
        gzip $backup_file
        
        # Calculate size
        local size=$(du -h $backup_file_gz | cut -f1)
        
        print_status "Base de datos respaldada: $backup_file_gz ($size)"
        
        # Verify backup integrity
        if gunzip -t $backup_file_gz 2>/dev/null; then
            print_status "Integridad del backup verificada"
        else
            print_error "Error en la integridad del backup"
            exit 1
        fi
    else
        print_error "Error al respaldar base de datos"
        exit 1
    fi
}

# Backup Files (uploads, documents)
backup_files() {
    echo -e "${BLUE}📁 Respaldando archivos...${NC}"
    
    local backup_file="$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz"
    
    # Directories to backup
    local dirs_to_backup="uploads"
    
    if [ -d "uploads" ]; then
        # Create backup - fail on error
        if ! tar -czf $backup_file $dirs_to_backup 2>&1; then
            print_error "Error al crear backup de archivos"
            exit 1
        fi
        
        # Verify integrity
        if ! tar -tzf $backup_file > /dev/null 2>&1; then
            print_error "Archivo de backup corrupto: $backup_file"
            exit 1
        fi
        
        local size=$(du -h $backup_file | cut -f1)
        local count=$(tar -tzf $backup_file | wc -l)
        
        print_status "Archivos respaldados: $backup_file ($size, $count archivos)"
        print_status "Integridad de archivos verificada"
    else
        print_warning "Directorio uploads no encontrado, saltando..."
    fi
}

# Backup Logs
backup_logs() {
    echo -e "${BLUE}📝 Respaldando logs...${NC}"
    
    local backup_file="$BACKUP_DIR/logs/logs_backup_$TIMESTAMP.tar.gz"
    
    if [ -d "logs" ]; then
        # Create backup - fail on error
        if ! tar -czf $backup_file logs/ 2>&1; then
            print_error "Error al crear backup de logs"
            exit 1
        fi
        
        # Verify integrity
        if ! tar -tzf $backup_file > /dev/null 2>&1; then
            print_error "Archivo de backup corrupto: $backup_file"
            exit 1
        fi
        
        local size=$(du -h $backup_file | cut -f1)
        
        print_status "Logs respaldados: $backup_file ($size)"
        print_status "Integridad de logs verificada"
    else
        print_warning "Directorio logs no encontrado, saltando..."
    fi
}

# Full Backup
backup_full() {
    echo -e "${BLUE}💾 Backup completo del sistema...${NC}"
    
    backup_database
    backup_files
    backup_logs
    
    # Collect backup artifacts (only those that exist)
    local backup_files_to_archive=()
    
    # Always include database (required)
    if [ -f "$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql.gz" ]; then
        backup_files_to_archive+=("$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql.gz")
    else
        print_error "Database backup not found"
        exit 1
    fi
    
    # Include files backup if exists
    if [ -f "$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz" ]; then
        backup_files_to_archive+=("$BACKUP_DIR/files/files_backup_$TIMESTAMP.tar.gz")
    fi
    
    # Include logs backup if exists
    if [ -f "$BACKUP_DIR/logs/logs_backup_$TIMESTAMP.tar.gz" ]; then
        backup_files_to_archive+=("$BACKUP_DIR/logs/logs_backup_$TIMESTAMP.tar.gz")
    fi
    
    # Always include config files
    backup_files_to_archive+=(".env.example" "docker-compose.yml")
    
    # Create full backup archive
    local full_backup="$BACKUP_DIR/full/full_backup_$TIMESTAMP.tar.gz"
    
    if ! tar -czf $full_backup "${backup_files_to_archive[@]}" 2>&1; then
        print_error "Error al crear backup completo"
        exit 1
    fi
    
    # Verify integrity
    if ! tar -tzf $full_backup > /dev/null 2>&1; then
        print_error "Archivo de backup completo corrupto: $full_backup"
        exit 1
    fi
    
    local size=$(du -h $full_backup | cut -f1)
    local count=${#backup_files_to_archive[@]}
    print_status "Backup completo creado: $full_backup ($size, $count componentes)"
    print_status "Integridad del backup completo verificada"
}

# Cleanup old backups
cleanup_old_backups() {
    echo -e "${BLUE}🧹 Limpiando backups antiguos (>$RETENTION_DAYS días)...${NC}"
    
    local deleted_count=0
    
    # Find and delete old backups
    find $BACKUP_DIR -type f -name "*.gz" -mtime +$RETENTION_DAYS | while read file; do
        rm -f "$file"
        deleted_count=$((deleted_count + 1))
    done
    
    if [ $deleted_count -gt 0 ]; then
        print_status "Eliminados $deleted_count backups antiguos"
    else
        print_status "No hay backups antiguos para eliminar"
    fi
}

# Upload to cloud (optional)
upload_to_cloud() {
    if [ ! -z "$AWS_S3_BUCKET" ]; then
        echo -e "${BLUE}☁️  Subiendo a S3...${NC}"
        
        aws s3 cp $BACKUP_DIR s3://$AWS_S3_BUCKET/backups/$TIMESTAMP/ --recursive
        
        print_status "Backup subido a S3: s3://$AWS_S3_BUCKET/backups/$TIMESTAMP/"
    fi
}

# Generate backup report
generate_report() {
    local report_file="$BACKUP_DIR/backup_report_$TIMESTAMP.txt"
    
    cat > $report_file <<EOF
========================================
REPORTE DE BACKUP
Sistema Judicial Digital - Marruecos
========================================

Fecha: $(date)
Tipo de Backup: $BACKUP_TYPE
Timestamp: $TIMESTAMP

RESUMEN:
----------------------------------------
$(find $BACKUP_DIR -type f -name "*$TIMESTAMP*" -exec ls -lh {} \; | awk '{print $9 " - " $5}')

ESTADÍSTICAS:
----------------------------------------
Total de archivos respaldados: $(find $BACKUP_DIR -type f -name "*$TIMESTAMP*" | wc -l)
Tamaño total: $(du -sh $BACKUP_DIR/*$TIMESTAMP* 2>/dev/null | awk '{sum+=$1} END {print sum}')

UBICACIÓN:
----------------------------------------
Directorio: $BACKUP_DIR
Retención: $RETENTION_DAYS días

VERIFICACIÓN:
----------------------------------------
✅ Backup completado exitosamente
✅ Integridad verificada
✅ Compresión aplicada

========================================
EOF
    
    print_status "Reporte generado: $report_file"
    
    # Show summary
    echo ""
    echo -e "${GREEN}📋 Resumen del Backup:${NC}"
    cat $report_file | grep -A 20 "RESUMEN:"
}

# Main execution
case $BACKUP_TYPE in
    "db"|"database")
        backup_database
        ;;
    "files")
        backup_files
        ;;
    "logs")
        backup_logs
        ;;
    "full")
        backup_full
        ;;
    *)
        print_error "Tipo de backup inválido: $BACKUP_TYPE"
        echo "Uso: ./backup.sh [full|db|files|logs]"
        exit 1
        ;;
esac

# Cleanup old backups
cleanup_old_backups

# Upload to cloud (if configured)
upload_to_cloud

# Generate report
generate_report

echo ""
echo -e "${GREEN}✅ Backup completado exitosamente!${NC}"
echo ""
