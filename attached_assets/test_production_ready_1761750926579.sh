#!/bin/bash
# test_production_ready.sh - Test Completo del Sistema para Producción

set -e

echo "🧪 TESTING COMPLETO DEL SISTEMA JUDICIAL DIGITAL - MARRUECOS"
echo "============================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
    ((TESTS_PASSED++))
}

error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
}

# Función para ejecutar test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TOTAL_TESTS++))
    log "Ejecutando: $test_name"
    
    if eval "$test_command"; then
        success "$test_name"
        return 0
    else
        error "$test_name"
        return 1
    fi
}

# Test 1: Verificar estructura del proyecto
test_project_structure() {
    local required_files=(
        "backend/app/main.py"
        "backend/app/config.py"
        "backend/app/models.py"
        "backend/app/database.py"
        "backend/app/auth/auth.py"
        "backend/app/auth/two_factor.py"
        "backend/app/auth/two_factor_standalone.py"
        "backend/app/config_production.py"
        "backend/requirements.txt"
        "backend/Dockerfile"
        "docker-compose.production.yml"
        ".env.production"
        "deploy_production.sh"
        "frontend/package.json"
        "frontend/src/App.js"
        "frontend/src/components/AdminDashboard.jsx"
        "frontend/src/components/Login.js"
        "frontend/src/components/TwoFactorSetup.js"
        "frontend/src/contexts/AuthContext.js"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            return 1
        fi
    done
    return 0
}

# Test 2: Verificar dependencias Python
test_python_dependencies() {
    cd backend
    python -c "
import sys
required_packages = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2', 'redis', 
    'python-jose', 'passlib', 'pydantic', 'pyotp', 'qrcode'
]
missing = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        missing.append(package)
if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
"
    cd ..
}

# Test 3: Verificar configuración de producción
test_production_config() {
    cd backend
    python -c "
from app.config_production import ProductionSettings
import os
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['ELASTICSEARCH_URL'] = 'http://localhost:9200'
os.environ['SECRET_KEY'] = 'test-secret-key-minimum-32-characters'
settings = ProductionSettings()
assert settings.app_name == 'Sistema Judicial Digital - Marruecos'
assert settings.environment == 'production'
assert settings.is_production == True
"
    cd ..
}

# Test 4: Verificar autenticación
test_authentication() {
    cd backend
    export $(cat .env.test | xargs)
    python -c "
from app.auth.auth import get_password_hash, verify_password, create_access_token, verify_token

# Test password hashing
password = 'TestPassword123'
hashed = get_password_hash(password)
assert verify_password(password, hashed)

# Test token generation
data = {'sub': 'test@justicia.ma', 'user_id': 1}
token = create_access_token(data)
payload = verify_token(token)
assert payload['sub'] == 'test@justicia.ma'
"
    cd ..
}

# Test 5: Verificar 2FA standalone
test_2fa_standalone() {
    cd backend
    export $(cat .env.test | xargs)
    python -c "
from app.auth.two_factor_standalone import TwoFactorAuthStandalone
import pyotp

# Test 2FA standalone
two_factor = TwoFactorAuthStandalone('test_2fa.json')
email = 'test@justicia.ma'

# Test secret generation
secret = two_factor.generate_secret_key(email)
assert len(secret) > 0

# Test QR code generation
qr_code = two_factor.generate_qr_code(email, secret)
assert qr_code.startswith('data:image/png;base64,')

# Test TOTP verification
totp = pyotp.TOTP(secret)
code = totp.now()
assert two_factor.verify_totp_code(secret, code, email)

# Cleanup
import os
if os.path.exists('test_2fa.json'):
    os.remove('test_2fa.json')
"
    cd ..
}

# Test 6: Verificar FastAPI endpoints
test_fastapi_endpoints() {
    cd backend
    export $(cat .env.test | xargs)
    python -c "
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test root endpoint
response = client.get('/', headers={'Host': 'localhost'})
assert response.status_code == 200

# Test health endpoint
response = client.get('/health', headers={'Host': 'localhost'})
assert response.status_code == 200
data = response.json()
assert data['status'] == 'healthy'

# Test metrics endpoint
response = client.get('/metrics', headers={'Host': 'localhost'})
assert response.status_code == 200
"
    cd ..
}

# Test 7: Verificar Docker Compose
test_docker_compose() {
    docker-compose -f docker-compose.production.yml config > /dev/null
}

# Test 8: Verificar scripts de deployment
test_deployment_scripts() {
    [ -x "deploy_production.sh" ]
    [ -f ".env.production" ]
    [ -f "docker-compose.production.yml" ]
}

# Test 9: Verificar frontend
test_frontend_structure() {
    [ -f "frontend/package.json" ]
    [ -f "frontend/src/App.js" ]
    [ -f "frontend/src/components/Login.js" ]
    [ -f "frontend/src/components/AdminDashboard.jsx" ]
    [ -f "frontend/src/contexts/AuthContext.js" ]
}

# Test 10: Verificar configuración de Marruecos
test_morocco_config() {
    cd backend
    python -c "
from app.config_production import MOROCCO_SPECIFIC_CONFIG
config = MOROCCO_SPECIFIC_CONFIG
assert config['country'] == 'Morocco'
assert config['country_code'] == 'MA'
assert 'ar' in config['languages']['primary']
assert 'fr' in config['languages']['secondary']
assert config['timezone'] == 'Africa/Casablanca'
"
    cd ..
}

# Ejecutar todos los tests
echo ""
log "Iniciando tests del sistema..."

run_test "Estructura del Proyecto" "test_project_structure"
run_test "Dependencias Python" "test_python_dependencies"
run_test "Configuración de Producción" "test_production_config"
run_test "Sistema de Autenticación" "test_authentication"
run_test "2FA Standalone" "test_2fa_standalone"
run_test "Endpoints FastAPI" "test_fastapi_endpoints"
run_test "Docker Compose" "test_docker_compose"
run_test "Scripts de Deployment" "test_deployment_scripts"
run_test "Estructura Frontend" "test_frontend_structure"
run_test "Configuración Marruecos" "test_morocco_config"

# Resumen final
echo ""
echo "============================================================="
echo "📊 RESUMEN DE TESTS"
echo "============================================================="
echo -e "Total de tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Tests exitosos: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests fallidos: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo "🎉 ¡TODOS LOS TESTS PASARON!"
    echo "✅ Sistema listo para producción"
    echo "🇲🇦 Sistema Judicial Digital preparado para Marruecos"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "   1. Configurar variables de entorno en .env.production"
    echo "   2. Ejecutar: ./deploy_production.sh"
    echo "   3. Configurar SSL certificates"
    echo "   4. Configurar HSM para firmas digitales"
    echo "   5. Configurar monitoreo con Grafana/Prometheus"
    exit 0
else
    echo ""
    echo "❌ ALGUNOS TESTS FALLARON"
    echo "Por favor revise los errores antes de proceder a producción"
    exit 1
fi
