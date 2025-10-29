#!/bin/bash

# setup-cron.sh - Configurar Backups Automáticos con Cron
# Sistema Judicial Digital - Marruecos

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}⏰ Configurando Backups Automáticos${NC}"
echo "=================================="

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default schedule: Daily at 2 AM
BACKUP_SCHEDULE="${BACKUP_SCHEDULE:-0 2 * * *}"

echo "Directorio del proyecto: $PROJECT_DIR"
echo "Schedule: $BACKUP_SCHEDULE (cron format)"
echo ""

# Create cron job
CRON_JOB="$BACKUP_SCHEDULE cd $PROJECT_DIR && $PROJECT_DIR/scripts/backup.sh full >> $PROJECT_DIR/logs/backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    echo -e "${GREEN}✅ Cron job ya existe${NC}"
    echo "Cron job actual:"
    crontab -l | grep "backup.sh"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo -e "${GREEN}✅ Cron job configurado exitosamente${NC}"
    echo ""
    echo "Backup automático configurado para ejecutarse:"
    echo "$BACKUP_SCHEDULE"
    echo ""
fi

# Show all cron jobs
echo ""
echo "Cron jobs actuales:"
echo "==================="
crontab -l

echo ""
echo -e "${GREEN}✅ Configuración completa!${NC}"
echo ""
echo "El backup se ejecutará automáticamente según el schedule configurado."
echo "Para verificar logs: tail -f $PROJECT_DIR/logs/backup.log"
echo ""
