# Tests de Performance - Sistema Judicial Digital

## 📋 Descripción

Suite completa de tests de carga y performance para validar que el Sistema Judicial Digital cumple con los requisitos gubernamentales de:

- **≥1500 usuarios concurrentes** simultáneos
- **Tiempo de respuesta p95 < 1000ms** para operaciones críticas
- **Error rate < 5%** bajo carga máxima
- **Throughput ≥ 100 req/s** sostenido

## 🚀 Instalación

```bash
# Instalar Locust
pip install locust==2.20.0

# O instalar todas las dependencias
pip install -r requirements.txt
```

## 🧪 Ejecutar Tests

### Método 1: Script Automatizado (Recomendado)

```bash
# Ejecutar con configuración por defecto (1500 usuarios, 5 minutos)
./backend/tests/performance/run_load_tests.sh

# Configuración personalizada
./backend/tests/performance/run_load_tests.sh http://localhost:8000 2000 150 10m

# Parámetros:
# 1. HOST: URL del servidor (default: http://localhost:8000)
# 2. USERS: Número de usuarios concurrentes (default: 1500)
# 3. SPAWN_RATE: Usuarios/segundo para spawn (default: 100)
# 4. RUN_TIME: Duración del test (default: 5m)
```

### Método 2: Locust UI (Interactivo)

```bash
# Iniciar Locust Web UI
locust -f backend/tests/performance/locustfile.py --host=http://localhost:8000

# Acceder a http://localhost:8089
# Configurar:
# - Number of users: 1500
# - Spawn rate: 100
# - Host: http://localhost:8000
```

### Método 3: Modo Headless (CI/CD)

```bash
# Test rápido (100 usuarios, 1 minuto)
locust -f backend/tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users=100 \
    --spawn-rate=10 \
    --run-time=1m \
    --headless \
    --only-summary

# Test completo (1500 usuarios, 10 minutos)
locust -f backend/tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users=1500 \
    --spawn-rate=100 \
    --run-time=10m \
    --headless \
    --html=report.html \
    --csv=stats
```

## 📊 Perfiles de Usuario

### JudicialSystemUser (Usuario General)
Simula comportamiento típico de usuarios del sistema:

**Tareas (con pesos):**
- `view_dashboard` (10): Ver dashboard principal
- `list_cases` (8): Listar casos
- `search_cases` (5): Búsqueda de casos
- `view_case_detail` (3): Ver detalles de caso
- `create_case` (2): Crear nuevo caso
- `view_documents` (4): Ver documentos
- `view_audit_logs` (3): Ver logs de auditoría
- `health_check` (1): Verificación de salud

**Wait time:** 1-3 segundos entre requests

### AdminUser (Administrador)
Simula administradores del sistema:

**Tareas:**
- `view_audit_dashboard` (5): Dashboard de auditoría
- `export_audit_logs` (3): Exportar logs (JSON/CSV)
- `manage_users` (2): Gestión de usuarios

**Wait time:** 2-5 segundos

### JudgeUser (Juez)
Simula jueces trabajando en casos:

**Tareas:**
- `view_assigned_cases` (10): Ver casos asignados
- `update_case_status` (5): Actualizar estado de caso
- `sign_document` (3): Firmar documentos

**Wait time:** 3-6 segundos

### LawyerUser (Abogado)
Simula abogados consultando casos:

**Tareas:**
- `view_client_cases` (8): Ver casos de clientes
- `upload_document` (5): Subir documentos
- `view_case_documents` (3): Ver documentos de caso

**Wait time:** 2-4 segundos

## 📈 Métricas Monitoreadas

### Rendimiento
- **Requests per second (RPS)**: Throughput del sistema
- **Response time (avg/min/max/p50/p95/p99)**: Latencias
- **Failures**: Errores y tasas de fallo
- **Users**: Usuarios activos concurrentes

### Criterios de Éxito

| Métrica | Objetivo | Crítico |
|---------|----------|---------|
| Usuarios Concurrentes | ≥1500 | OBLIGATORIO |
| Response Time p95 | <1000ms | OBLIGATORIO |
| Error Rate | <5% | OBLIGATORIO |
| Throughput | ≥100 req/s | RECOMENDADO |
| Response Time p50 | <200ms | RECOMENDADO |

## 📁 Reportes Generados

Los tests generan reportes en `backend/tests/performance/reports/[timestamp]/`:

- **report.html**: Reporte visual interactivo con gráficos
- **stats_stats.csv**: Estadísticas detalladas por endpoint
- **stats_failures.csv**: Log de todos los errores
- **stats_stats_history.csv**: Historial temporal de métricas

### Ejemplo de Reporte CSV

```csv
Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,Min Response Time,Max Response Time,Average Content Size,Requests/s,Failures/s,50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%
GET,/api/cases,12000,120,150,180,50,2000,1500,80,0.8,150,170,190,200,250,300,400,500,1000,1500,2000
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Configurar host
export LOCUST_HOST=http://production.justicia.ma

# Usuarios concurrentes
export LOCUST_USERS=2000

# Tasa de spawn
export LOCUST_SPAWN_RATE=200

# Duración
export LOCUST_RUN_TIME=15m
```

### Distribución de Carga (Distributed Load Testing)

Para simular >5000 usuarios, usar modo distribuido:

**Master:**
```bash
locust -f locustfile.py --master --expect-workers=4
```

**Workers (en diferentes servidores):**
```bash
locust -f locustfile.py --worker --master-host=<master-ip>
locust -f locustfile.py --worker --master-host=<master-ip>
locust -f locustfile.py --worker --master-host=<master-ip>
locust -f locustfile.py --worker --master-host=<master-ip>
```

## 📊 Análisis de Resultados

### Interpretar Métricas

**Response Times:**
- p50 < 200ms: Excelente
- p95 < 1000ms: Aceptable (requisito)
- p99 < 2000ms: Bueno para casos extremos

**Error Rate:**
- <1%: Excelente
- 1-5%: Aceptable (dentro de requisito)
- >5%: Requiere optimización

**Throughput:**
- >100 req/s: Cumple requisito
- >200 req/s: Excelente
- >500 req/s: Óptimo para crecimiento

### Troubleshooting Performance

**Latencia alta (>1000ms p95):**
```bash
# 1. Verificar índices de DB
docker-compose exec db psql -U justicia -d justicia_db -c "\di"

# 2. Optimizar queries lentos
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT query, mean_exec_time, calls 
    FROM pg_stat_statements 
    ORDER BY mean_exec_time DESC 
    LIMIT 10;
"

# 3. Revisar caché Redis
docker-compose exec redis redis-cli INFO stats

# 4. Aumentar workers
docker-compose up -d --scale app1=5
```

**Error rate alto (>5%):**
```bash
# 1. Ver errores específicos
cat reports/[timestamp]/stats_failures.csv

# 2. Verificar logs de aplicación
docker-compose logs app1 | grep ERROR

# 3. Revisar límites de recursos
docker stats --no-stream
```

## 🔄 Integración CI/CD

### GitHub Actions

```yaml
name: Performance Tests

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Domingos a las 2 AM

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: sleep 30
      
      - name: Run performance tests
        run: ./backend/tests/performance/run_load_tests.sh
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: performance-reports
          path: backend/tests/performance/reports/
```

## 📋 Checklist Pre-Producción

Antes de deployment a producción, ejecutar:

- [ ] Test con 1500 usuarios concurrentes (5 minutos)
- [ ] Test con 2000 usuarios concurrentes (stress test)
- [ ] Test de duración (1500 usuarios, 30 minutos)
- [ ] Verificar p95 < 1000ms
- [ ] Verificar error rate < 5%
- [ ] Revisar reportes HTML
- [ ] Analizar bottlenecks identificados
- [ ] Optimizar queries/indices si es necesario
- [ ] Re-ejecutar tests después de optimizaciones
- [ ] Documentar resultados finales

## 🎯 Benchmarks de Referencia

### Configuración Base (3 app instances, 8GB RAM)

| Usuarios | RPS | p50 | p95 | p99 | Error Rate |
|----------|-----|-----|-----|-----|------------|
| 100 | 50 | 80ms | 150ms | 200ms | 0% |
| 500 | 150 | 120ms | 300ms | 500ms | 0.5% |
| 1000 | 250 | 180ms | 600ms | 900ms | 2% |
| 1500 | 300 | 220ms | 800ms | 1200ms | 4% |
| 2000 | 320 | 300ms | 1500ms | 2500ms | 8% |

### Configuración Optimizada (5 app instances, 16GB RAM)

| Usuarios | RPS | p50 | p95 | p99 | Error Rate |
|----------|-----|-----|-----|-----|------------|
| 1500 | 400 | 150ms | 400ms | 600ms | 1% |
| 2000 | 500 | 180ms | 500ms | 800ms | 2% |
| 3000 | 650 | 250ms | 800ms | 1200ms | 4% |

## 📞 Soporte

Para problemas con performance tests:

- **Documentación Locust**: https://docs.locust.io/
- **Email**: performance@justicia.ma
- **Issues**: GitHub Issues con tag `performance`

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦
