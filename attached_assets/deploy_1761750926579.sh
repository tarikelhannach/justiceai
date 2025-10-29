#!/bin/bash

# deploy.sh - Script de Deployment para Sistema Judicial Digital Marruecos
# Uso: ./deploy.sh [development|staging|production]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Sistema Judicial Digital - Marruecos"
DEFAULT_ENV="development"
ENV=${1:-$DEFAULT_ENV}

echo -e "${BLUE}🏛️ Deploying ${PROJECT_NAME}${NC}"
echo -e "${BLUE}Environment: ${ENV}${NC}"
echo "=================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_status "Docker Compose is installed"
    
    # Check .env file
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        read -p "Press enter to continue after editing .env file..."
    fi
    print_status ".env file exists"
}

# Setup directories
setup_directories() {
    echo -e "${BLUE}📁 Setting up directories...${NC}"
    
    mkdir -p uploads logs temp ssl hsm
    chmod 755 uploads logs temp
    chmod 700 ssl hsm  # More restrictive for sensitive directories
    
    # Create log files
    touch logs/justicia.log
    touch logs/nginx.log
    
    print_status "Directories created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    if [ "$ENV" = "development" ] && [ ! -f ssl/justicia.crt ]; then
        echo -e "${BLUE}🔒 Generating self-signed SSL certificates for development...${NC}"
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/justicia.key \
            -out ssl/justicia.crt \
            -subj "/C=MA/ST=Rabat/L=Rabat/O=Ministry of Justice/OU=IT Department/CN=localhost"
        
        print_status "SSL certificates generated"
    elif [ "$ENV" = "production" ] && [ ! -f ssl/justicia.crt ]; then
        print_warning "Production SSL certificates not found in ssl/ directory"
        print_warning "Please obtain valid SSL certificates from a CA"
    fi
}

# Database initialization
init_database() {
    echo -e "${BLUE}🗄️ Initializing database...${NC}"
    
    # Create init-db.sql script
    cat > init-db.sql << 'EOF'
-- Initialization script for Justicia Digital Morocco Database
-- Configuración específica para sistema judicial marroquí

-- Extensions for full-text search in Arabic
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Arabic text search configuration
CREATE TEXT SEARCH CONFIGURATION arabic_custom (COPY = arabic);

-- Create custom indexes for better performance with Arabic text
-- These will be created by the application, but we ensure the database supports them

-- Set default timezone for Morocco
SET timezone = 'Africa/Casablanca';

-- Create audit schema for compliance
CREATE SCHEMA IF NOT EXISTS audit;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE justicia_db TO justicia;
GRANT ALL PRIVILEGES ON SCHEMA public TO justicia;
GRANT ALL PRIVILEGES ON SCHEMA audit TO justicia;

EOF
    
    print_status "Database initialization script created"
}

# Choose docker-compose file based on environment
get_compose_file() {
    case $ENV in
        "development")
            echo "docker-compose.yml"
            ;;
        "staging")
            echo "docker-compose.staging.yml"
            ;;
        "production")
            echo "docker-compose.production.yml"
            ;;
        *)
            echo "docker-compose.yml"
            ;;
    esac
}

# Deploy based on environment
deploy() {
    local compose_file=$(get_compose_file)
    
    echo -e "${BLUE}🚀 Deploying with ${compose_file}...${NC}"
    
    # Stop existing containers
    if [ -f $compose_file ]; then
        echo -e "${YELLOW}Stopping existing containers...${NC}"
        docker-compose -f $compose_file down
    fi
    
    # Build and start containers
    echo -e "${BLUE}Building and starting containers...${NC}"
    docker-compose -f $compose_file up --build -d
    
    print_status "Containers started"
    
    # Wait for services to be ready
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    sleep 30
    
    # Check health
    check_services_health
}

# Check services health
check_services_health() {
    echo -e "${BLUE}🏥 Checking services health...${NC}"
    
    # Check main application
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Main application is healthy"
    else
        print_error "Main application health check failed"
        show_logs
        exit 1
    fi
    
    # Check database
    if docker-compose exec -T db pg_isready -U justicia > /dev/null 2>&1; then
        print_status "Database is ready"
    else
        print_warning "Database might not be ready yet"
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        print_status "Redis is ready"
    else
        print_warning "Redis might not be ready yet"
    fi
    
    # Check Elasticsearch
    if curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        print_status "Elasticsearch is ready"
    else
        print_warning "Elasticsearch might not be ready yet"
    fi
}

# Show logs for debugging
show_logs() {
    echo -e "${YELLOW}📋 Recent logs:${NC}"
    docker-compose logs --tail=20 app1
}

# Setup development environment
setup_development() {
    echo -e "${BLUE}🔧 Setting up development environment...${NC}"
    
    # Install pre-commit hooks if in a git repository
    if [ -d .git ] && command -v pre-commit &> /dev/null; then
        pre-commit install
        print_status "Pre-commit hooks installed"
    fi
    
    # Create development database
    print_status "Development environment configured"
}

# Setup production environment
setup_production() {
    echo -e "${BLUE}🏭 Setting up production environment...${NC}"
    
    # Security checks
    if [ ! -f ssl/justicia.crt ] || [ ! -f ssl/justicia.key ]; then
        print_error "Production SSL certificates are required!"
        print_error "Place your certificates in ssl/justicia.crt and ssl/justicia.key"
        exit 1
    fi
    
    # Check environment variables
    if grep -q "change-this" .env; then
        print_error "Please update all placeholder values in .env file!"
        exit 1
    fi
    
    # Set secure permissions
    chmod 600 .env
    chmod 600 ssl/justicia.key
    
    print_status "Production environment configured"
}

# Cleanup function
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    # Remove temporary files
    [ -f init-db.sql ] && rm init-db.sql
    
    # Clean up Docker if requested
    read -p "Clean up unused Docker images? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -f
        print_status "Docker cleanup completed"
    fi
}

# Main deployment flow
main() {
    echo -e "${GREEN}Starting deployment for ${ENV} environment...${NC}"
    
    # Pre-deployment checks
    check_prerequisites
    setup_directories
    generate_ssl_certs
    init_database
    
    # Environment-specific setup
    case $ENV in
        "development")
            setup_development
            ;;
        "production")
            setup_production
            ;;
    esac
    
    # Deploy
    deploy
    
    # Post-deployment info
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Service URLs:${NC}"
    echo "  🏛️  Main Application: http://localhost:8000"
    echo "  📊 API Documentation: http://localhost:8000/docs"
    echo "  🏥 Health Check: http://localhost:8000/health"
    echo "  📈 Metrics: http://localhost:8000/metrics"
    echo "  🗃️  Redis Commander: http://localhost:8081"
    echo "  🔍 Elasticsearch Head: http://localhost:9100"
    echo "  🌺 Celery Flower: http://localhost:5555"
    echo "  📊 Grafana: http://localhost:3000 (admin/admin123)"
    echo ""
    echo -e "${BLUE}📁 Important directories:${NC}"
    echo "  📄 Uploads: ./uploads/"
    echo "  📋 Logs: ./logs/"
    echo "  🔒 SSL: ./ssl/"
    echo ""
    echo -e "${YELLOW}⚠️  Next steps:${NC}"
    echo "  1. Configure your HSM settings in .env if using hardware HSM"
    echo "  2. Update SSL certificates for production deployment"
    echo "  3. Configure monitoring and alerting"
    echo "  4. Setup backup procedures"
    echo "  5. Review security settings"
    echo ""
    echo -e "${GREEN}🇲🇦 Sistema Judicial Digital listo para Marruecos!${NC}"
}

# Script execution
case "${1:-}" in
    "clean")
        cleanup
        exit 0
        ;;
    "logs")
        show_logs
        exit 0
        ;;
    "health")
        check_services_health
        exit 0
        ;;
    *)
        main
        ;;
esac