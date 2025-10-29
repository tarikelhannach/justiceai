#!/bin/bash

# Quick Performance Test Runner
# Sistema Judicial Digital - Marruecos

cd "$(dirname "$0")"

echo "🚀 Iniciando tests de performance..."
echo ""
echo "NOTA: Este es un test de concepto."
echo "Para tests completos (≥1500 usuarios), usar:"
echo "  ./tests/performance/run_load_tests.sh"
echo ""

# Test rápido con menos usuarios para validar setup
locust \
    -f tests/performance/locustfile.py \
    --host="${1:-http://localhost:8000}" \
    --users=100 \
    --spawn-rate=10 \
    --run-time=1m \
    --headless \
    --only-summary

echo ""
echo "✓ Test de concepto completado"
echo ""
echo "Para ejecutar test completo de producción (≥1500 usuarios):"
echo "  ./tests/performance/run_load_tests.sh http://localhost:8000 1500 100 5m"
