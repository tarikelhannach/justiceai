#!/bin/bash
# deploy_production.sh - Script de Deployment para Producción

set -e

echo "🚀 Iniciando deployment del Sistema Judicial Digital - Marruecos"
echo "================================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar prerrequisitos
check_prerequisites() {
    log "Verificando prerrequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado"
        exit 1
    fi
    
    # Verificar archivo .env.production
    if [ ! -f ".env.production" ]; then
        error "Archivo .env.production no encontrado"
        exit 1
    fi
    
    success "Prerrequisitos verificados"
}

# Crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    mkdir -p logs/{nginx,app,celery}
    mkdir -p uploads
    mkdir -p backups/{postgres,app}
    mkdir -p ssl
    mkdir -p monitoring/{prometheus,grafana,fluentd}
    
    success "Directorios creados"
}

# Configurar SSL
setup_ssl() {
    log "Configurando certificados SSL..."
    
    if [ ! -f "ssl/justicia.ma.crt" ] || [ ! -f "ssl/justicia.ma.key" ]; then
        warning "Certificados SSL no encontrados, generando certificados autofirmados..."
        
        # Generar certificado autofirmado
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/justicia.ma.key \
            -out ssl/justicia.ma.crt \
            -subj "/C=MA/ST=Rabat/L=Rabat/O=Ministry of Justice/OU=IT Department/CN=justicia.ma"
        
        success "Certificados SSL generados"
    else
        success "Certificados SSL encontrados"
    fi
}

# Configurar base de datos
setup_database() {
    log "Configurando base de datos..."
    
    # Crear script de inicialización
    cat > init-scripts/01-init.sql << 'SQL'
-- Inicialización de la base de datos para el Sistema Judicial Digital
-- Marruecos

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Configurar timezone
SET timezone = 'Africa/Casablanca';

-- Crear usuario de aplicación si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'justicia_app') THEN
        CREATE ROLE justicia_app WITH LOGIN PASSWORD 'app_password';
    END IF;
END
$$;

-- Otorgar permisos
GRANT CONNECT ON DATABASE justicia_prod TO justicia_app;
GRANT USAGE ON SCHEMA public TO justicia_app;
GRANT CREATE ON SCHEMA public TO justicia_app;
SQL

    success "Base de datos configurada"
}

# Configurar monitoreo
setup_monitoring() {
    log "Configurando monitoreo..."
    
    # Configuración de Prometheus
    cat > monitoring/prometheus/prometheus.yml << 'YAML'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'justicia-app'
    static_configs:
      - targets: ['app1:8000', 'app2:8000', 'app3:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']
YAML

    # Configuración de Grafana
    mkdir -p monitoring/grafana/provisioning/{datasources,dashboards}
    
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'YAML'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
YAML

    success "Monitoreo configurado"
}

# Deploy de la aplicación
deploy_application() {
    log "Desplegando aplicación..."
    
    # Parar contenedores existentes
    docker-compose -f docker-compose.production.yml down || true
    
    # Construir imágenes
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Iniciar servicios
    docker-compose -f docker-compose.production.yml up -d
    
    success "Aplicación desplegada"
}

# Verificar salud del sistema
health_check() {
    log "Verificando salud del sistema..."
    
    # Esperar a que los servicios estén listos
    sleep 30
    
    # Verificar aplicación
    if curl -f http://localhost/health > /dev/null 2>&1; then
        success "Aplicación principal: ✅"
    else
        error "Aplicación principal: ❌"
    fi
    
    # Verificar base de datos
    if docker exec justicia_postgres pg_isready -U justicia -d justicia_prod > /dev/null 2>&1; then
        success "Base de datos: ✅"
    else
        error "Base de datos: ❌"
    fi
    
    # Verificar Redis
    if docker exec justicia_redis redis-cli ping > /dev/null 2>&1; then
        success "Redis: ✅"
    else
        error "Redis: ❌"
    fi
    
    # Verificar Elasticsearch
    if curl -f http://localhost:9200/_health > /dev/null 2>&1; then
        success "Elasticsearch: ✅"
    else
        error "Elasticsearch: ❌"
    fi
}

# Mostrar información del deployment
show_deployment_info() {
    echo ""
    echo "🎉 Deployment completado exitosamente!"
    echo "======================================"
    echo ""
    echo "📊 Servicios disponibles:"
    echo "  • Aplicación Principal: https://justicia.ma"
    echo "  • API Documentation: https://justicia.ma/docs"
    echo "  • Health Check: https://justicia.ma/health"
    echo "  • Metrics: https://justicia.ma/metrics"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo "🔐 Credenciales por defecto:"
    echo "  • Grafana: admin / $(grep GRAFANA_PASSWORD .env.production | cut -d'=' -f2)"
    echo "  • Base de datos: justicia / $(grep DB_PASSWORD .env.production | cut -d'=' -f2)"
    echo ""
    echo "📝 Logs:"
    echo "  • Aplicación: docker logs justicia_app1"
    echo "  • Base de datos: docker logs justicia_postgres"
    echo "  • Redis: docker logs justicia_redis"
    echo ""
    echo "🛠️  Comandos útiles:"
    echo "  • Ver logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "  • Parar: docker-compose -f docker-compose.production.yml down"
    echo "  • Reiniciar: docker-compose -f docker-compose.production.yml restart"
    echo ""
    echo "🇲🇦 ¡Sistema Judicial Digital listo para Marruecos!"
}

# Función principal
main() {
    check_prerequisites
    create_directories
    setup_ssl
    setup_database
    setup_monitoring
    deploy_application
    health_check
    show_deployment_info
}

# Ejecutar función principal
main "$@"
