#!/bin/bash

# format.sh - Script para formatear código automáticamente

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🎨 Formateando código...${NC}\n"

# 1. isort - Ordenar imports
echo -e "${YELLOW}▶ Ordenando imports con isort...${NC}"
isort app/ tests/
echo -e "${GREEN}✓ Imports ordenados${NC}\n"

# 2. Black - Formatear código
echo -e "${YELLOW}▶ Formateando código con Black...${NC}"
black app/ tests/
echo -e "${GREEN}✓ Código formateado${NC}\n"

# 3. Verificar con Flake8
echo -e "${YELLOW}▶ Verificando con Flake8...${NC}"
if flake8 app/ tests/; then
    echo -e "${GREEN}✓ Flake8 OK${NC}\n"
else
    echo -e "${YELLOW}⚠ Revisa los warnings de Flake8${NC}\n"
fi

echo -e "${GREEN}✨ Formateo completado!${NC}"
