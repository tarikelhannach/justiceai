#!/bin/bash
# run_tests.sh - Script de Ejecución de Tests para Sistema Judicial Digital

set -e

echo "🏛️  Sistema Judicial Digital - Marruecos"
echo "========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Verificar instalación de pytest
if ! command -v pytest &> /dev/null; then
    print_error "pytest no está instalado. Instalando..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Limpiar archivos de caché
print_message "Limpiando archivos de caché..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
rm -rf .pytest_cache htmlcov .coverage coverage.xml 2>/dev/null || true

# Función para ejecutar tests
run_tests() {
    local test_type=$1
    local test_path=$2
    local marker=$3
    
    echo ""
    print_message "Ejecutando tests: $test_type"
    echo "========================================="
    
    if [ -n "$marker" ]; then
        pytest $test_path -m "$marker" --tb=short || {
            print_error "Falló: $test_type"
            return 1
        }
    else
        pytest $test_path --tb=short || {
            print_error "Falló: $test_type"
            return 1
        }
    fi
    
    print_message "Completado: $test_type"
    return 0
}

# Verificar argumento
case "${1:-all}" in
    unit)
        print_message "Ejecutando solo tests unitarios..."
        run_tests "Tests Unitarios" "tests/unit" "unit"
        ;;
    
    integration)
        print_message "Ejecutando tests de integración..."
        run_tests "Tests de Integración" "tests/integration" "integration"
        ;;
    
    security)
        print_message "Ejecutando tests de seguridad..."
        run_tests "Tests de Seguridad" "tests/security" "security"
        ;;
    
    api)
        print_message "Ejecutando tests de API..."
        run_tests "Tests de API" "tests/api" "api"
        ;;
    
    performance)
        print_warning "Ejecutando tests de performance (puede tardar)..."
        run_tests "Tests de Performance" "tests/performance" "performance"
        ;;
    
    rbac)
        print_message "Ejecutando tests de RBAC..."
        run_tests "Tests de RBAC" "tests" "rbac"
        ;;
    
    smoke)
        print_message "Ejecutando tests de humo (smoke tests)..."
        run_tests "Smoke Tests" "tests" "smoke"
        ;;
    
    coverage)
        print_message "Generando reporte de cobertura completo..."
        pytest tests/ --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
        print_message "Reporte HTML generado en: htmlcov/index.html"
        print_message "Reporte XML generado en: coverage.xml"
        ;;
    
    all)
        print_message "Ejecutando TODOS los tests..."
        echo ""
        
        # Tests unitarios
        run_tests "1/6 - Tests Unitarios" "tests/unit" "unit"
        
        # Tests de API
        run_tests "2/6 - Tests de API" "tests/api" "api"
        
        # Tests de integración
        run_tests "3/6 - Tests de Integración" "tests/integration" "integration"
        
        # Tests de seguridad
        run_tests "4/6 - Tests de Seguridad" "tests/security" "security"
        
        # Tests de RBAC
        run_tests "5/6 - Tests de RBAC" "tests" "rbac"
        
        # Coverage final
        print_message "6/6 - Generando reporte de cobertura..."
        pytest tests/ --cov=app --cov-report=term-missing --cov-report=html --cov-report=xml
        
        echo ""
        echo "========================================="
        print_message "Todos los tests completados exitosamente"
        print_message "Reporte de cobertura: htmlcov/index.html"
        echo "========================================="
        ;;
    
    *)
        echo "Uso: $0 {unit|integration|security|api|performance|rbac|smoke|coverage|all}"
        echo ""
        echo "Opciones:"
        echo "  unit         - Tests unitarios"
        echo "  integration  - Tests de integración"
        echo "  security     - Tests de seguridad"
        echo "  api          - Tests de API"
        echo "  performance  - Tests de performance"
        echo "  rbac         - Tests de control de acceso"
        echo "  smoke        - Tests rápidos de verificación"
        echo "  coverage     - Reporte de cobertura"
        echo "  all          - Todos los tests (por defecto)"
        exit 1
        ;;
esac

exit 0
