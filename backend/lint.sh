#!/bin/bash

# lint.sh - Script de linting y formateo de código

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Iniciando análisis de calidad de código...${NC}\n"

# Función para ejecutar comando y capturar resultado
run_check() {
    local name=$1
    shift
    echo -e "${YELLOW}▶ $name${NC}"
    if "$@"; then
        echo -e "${GREEN}✓ $name: PASSED${NC}\n"
        return 0
    else
        echo -e "${RED}✗ $name: FAILED${NC}\n"
        return 1
    fi
}

# Contador de errores
ERRORS=0

# 1. Black - Formateo de código
if ! run_check "Black (formateo)" black --check --diff app/ tests/; then
    echo -e "${YELLOW}💡 Ejecuta: black app/ tests/${NC}\n"
    ((ERRORS++))
fi

# 2. isort - Ordenar imports
if ! run_check "isort (imports)" isort --check-only --diff app/ tests/; then
    echo -e "${YELLOW}💡 Ejecuta: isort app/ tests/${NC}\n"
    ((ERRORS++))
fi

# 3. Flake8 - Linting
if ! run_check "Flake8 (linting)" flake8 app/ tests/; then
    ((ERRORS++))
fi

# 4. Mypy - Type checking
if ! run_check "Mypy (type checking)" mypy app/; then
    ((ERRORS++))
fi

# 5. Bandit - Security
if ! run_check "Bandit (security)" bandit -r app/ -c pyproject.toml; then
    ((ERRORS++))
fi

# 6. Pytest - Tests
if ! run_check "Pytest (tests)" pytest tests/ -m "smoke" --tb=short; then
    ((ERRORS++))
fi

# Resumen
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Todos los checks pasaron exitosamente!${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS check(s) fallaron${NC}"
    echo -e "${YELLOW}Por favor corrige los errores antes de commitear${NC}"
    exit 1
fi
