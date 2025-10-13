#!/bin/bash

# Sistema Judicial Digital - Performance Load Tests
# Tests de carga para validar ≥1500 usuarios concurrentes

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuración
HOST="${1:-http://localhost:8000}"
USERS="${2:-1500}"
SPAWN_RATE="${3:-100}"
RUN_TIME="${4:-5m}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  SISTEMA JUDICIAL - PERFORMANCE TESTS     ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "${BLUE}Configuración:${NC}"
echo -e "  Host: ${YELLOW}$HOST${NC}"
echo -e "  Usuarios: ${YELLOW}$USERS${NC}"
echo -e "  Spawn Rate: ${YELLOW}$SPAWN_RATE/s${NC}"
echo -e "  Duración: ${YELLOW}$RUN_TIME${NC}"
echo ""

# Verificar que el sistema esté activo
echo -e "${BLUE}Verificando sistema...${NC}"
if ! curl -sf "$HOST/health" > /dev/null; then
    echo -e "${RED}ERROR: Sistema no responde en $HOST${NC}"
    echo -e "${YELLOW}Asegúrate de que el sistema esté ejecutándose:${NC}"
    echo -e "  ${YELLOW}docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Sistema activo${NC}"
echo ""

# Crear directorio de reportes
REPORT_DIR="./reports/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

echo -e "${BLUE}Ejecutando tests de carga...${NC}"
echo -e "${YELLOW}Los reportes se guardarán en: $REPORT_DIR${NC}"
echo ""

# Ejecutar Locust en modo headless
locust \
    -f backend/tests/performance/locustfile.py \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="$RUN_TIME" \
    --html="$REPORT_DIR/report.html" \
    --csv="$REPORT_DIR/stats" \
    --headless \
    --only-summary

# Analizar resultados
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  ANÁLISIS DE RESULTADOS                   ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Leer estadísticas del CSV
if [ -f "$REPORT_DIR/stats_stats.csv" ]; then
    echo -e "${BLUE}Estadísticas principales:${NC}"
    cat "$REPORT_DIR/stats_stats.csv" | column -t -s ','
    echo ""
fi

# Verificar criterios de éxito
echo -e "${BLUE}Verificando criterios de éxito:${NC}"
echo ""

SUCCESS=true

# Criterio 1: ≥1500 usuarios concurrentes
if [ "$USERS" -ge 1500 ]; then
    echo -e "${GREEN}✓ Usuarios concurrentes: $USERS (≥1500)${NC}"
else
    echo -e "${RED}✗ Usuarios concurrentes: $USERS (<1500)${NC}"
    SUCCESS=false
fi

# Criterio 2: Tiempo de respuesta p95 < 1000ms (OBLIGATORIO)
# (extraer del CSV si existe)
if [ -f "$REPORT_DIR/stats_stats.csv" ]; then
    P95_TIME=$(awk -F',' 'NR>1 && $1 == "Aggregated" {print $10}' "$REPORT_DIR/stats_stats.csv")
    if [ ! -z "$P95_TIME" ]; then
        if (( $(echo "$P95_TIME < 1000" | bc -l) )); then
            echo -e "${GREEN}✓ Tiempo de respuesta p95: ${P95_TIME}ms (<1000ms)${NC}"
        else
            echo -e "${RED}✗ Tiempo de respuesta p95: ${P95_TIME}ms (≥1000ms) - OBLIGATORIO${NC}"
            SUCCESS=false
        fi
    else
        echo -e "${RED}✗ No se pudo medir p95 - OBLIGATORIO${NC}"
        SUCCESS=false
    fi
else
    echo -e "${RED}✗ No se encontraron estadísticas CSV - OBLIGATORIO${NC}"
    SUCCESS=false
fi

# Criterio 3: Error rate < 5%
if [ -f "$REPORT_DIR/stats_stats.csv" ]; then
    FAIL_RATE=$(awk -F',' 'NR>1 && $1 == "Aggregated" {
        total=$3+$4; 
        if (total > 0) print ($4/total)*100; 
        else print 0
    }' "$REPORT_DIR/stats_stats.csv")
    
    if [ ! -z "$FAIL_RATE" ]; then
        if (( $(echo "$FAIL_RATE < 5" | bc -l) )); then
            echo -e "${GREEN}✓ Error rate: ${FAIL_RATE}% (<5%)${NC}"
        else
            echo -e "${RED}✗ Error rate: ${FAIL_RATE}% (>5%)${NC}"
            SUCCESS=false
        fi
    fi
fi

echo ""
echo -e "${BLUE}Reportes generados:${NC}"
echo -e "  ${YELLOW}HTML Report: $REPORT_DIR/report.html${NC}"
echo -e "  ${YELLOW}CSV Stats: $REPORT_DIR/stats_stats.csv${NC}"
echo -e "  ${YELLOW}CSV Failures: $REPORT_DIR/stats_failures.csv${NC}"
echo ""

if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  ✓ TESTS DE PERFORMANCE EXITOSOS          ${NC}"
    echo -e "${GREEN}============================================${NC}"
    exit 0
else
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  ✗ TESTS DE PERFORMANCE FALLIDOS          ${NC}"
    echo -e "${RED}============================================${NC}"
    exit 1
fi
