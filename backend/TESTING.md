# Testing Infrastructure - Sistema Judicial Digital Marruecos

## 📋 Resumen Ejecutivo

Este documento describe la infraestructura de testing completa para el Sistema Judicial Digital de Marruecos, diseñada para cumplir con estándares gubernamentales de calidad y seguridad.

## 🎯 Objetivos de Cobertura

- **Cobertura de Código**: ≥95% (objetivo gubernamental)
- **Cobertura RBAC**: 100% de combinaciones rol-permiso
- **Cobertura de Seguridad**: Todos los vectores de ataque conocidos
- **Cobertura de Integración**: Todos los servicios externos

## 📁 Estructura de Tests

```
backend/tests/
├── conftest.py              # Fixtures globales y configuración
├── pytest.ini               # Configuración de pytest
├── .coveragerc             # Configuración de coverage
├── run_tests.sh            # Script de ejecución
│
├── unit/                   # Tests Unitarios
│   ├── test_auth.py       # Autenticación y seguridad
│   ├── test_cases.py      # Lógica de casos
│   ├── test_documents.py  # Gestión de documentos
│   └── test_users.py      # Gestión de usuarios
│
├── integration/            # Tests de Integración
│   ├── test_database.py   # PostgreSQL
│   ├── test_redis.py      # Caching y rate limiting
│   └── test_elasticsearch.py  # Búsqueda semántica
│
├── api/                    # Tests de API
│   ├── test_api_auth.py   # Endpoints de autenticación
│   ├── test_api_cases_rbac.py     # Casos con RBAC
│   ├── test_api_users_rbac.py     # Usuarios con RBAC
│   └── test_api_documents_rbac.py # Documentos con RBAC
│
├── security/               # Tests de Seguridad
│   ├── test_security.py   # Ataques generales
│   └── test_security_rbac.py  # Seguridad RBAC
│
└── performance/            # Tests de Performance (TBD)
    └── test_load.py       # Carga y concurrencia
```

## 🔧 Fixtures Disponibles

### Usuarios por Rol (Gobierno de Marruecos)
```python
# Fixtures de usuarios
admin_user       # Administrador del sistema
judge_user       # Juez
lawyer_user      # Abogado
clerk_user       # Secretario Judicial
citizen_user     # Ciudadano

# Fixtures de autenticación
admin_token, admin_headers
judge_token, judge_headers
lawyer_token, lawyer_headers
clerk_token, clerk_headers
citizen_token, citizen_headers
```

### Datos de Prueba
```python
sample_case      # Caso judicial de ejemplo
sample_document  # Documento de ejemplo
mock_redis       # Mock de Redis
mock_elasticsearch  # Mock de Elasticsearch
mock_hsm         # Mock de HSM para firmas
```

## 🚀 Ejecución de Tests

### Todos los Tests
```bash
cd backend
./run_tests.sh all
```

### Por Categoría
```bash
./run_tests.sh unit          # Tests unitarios
./run_tests.sh integration   # Tests de integración
./run_tests.sh api           # Tests de API
./run_tests.sh security      # Tests de seguridad
./run_tests.sh performance   # Tests de performance
./run_tests.sh rbac          # Tests RBAC específicos
```

### Coverage Report
```bash
./run_tests.sh coverage      # Genera reporte HTML
open htmlcov/index.html      # Ver reporte
```

### Smoke Tests (Rápidos)
```bash
./run_tests.sh smoke         # Verificación rápida
```

## 🔒 Tests de Seguridad RBAC

### Matriz de Permisos Completa

| Operación | Admin | Clerk | Judge | Lawyer | Citizen |
|-----------|:-----:|:-----:|:-----:|:------:|:-------:|
| **Casos** |
| Listar todos | ✅ | ✅ | ❌ | ❌ | ❌ |
| Listar propios | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver cualquiera | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver asignados | ✅ | ✅ | ✅ | ❌ | ❌ |
| Crear caso | ✅ | ✅ | ✅ | ✅ | ✅ |
| Asignar juez | ✅ | ✅ | ❌ | ❌ | ❌ |
| Cambiar estado | ✅ | ✅ | ✅* | ❌ | ❌ |
| Eliminar | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Documentos** |
| Listar todos | ✅ | ✅ | ❌ | ❌ | ❌ |
| Subir a caso | ✅ | ✅ | ✅* | ✅* | ✅* |
| Descargar | ✅ | ✅ | ✅* | ✅* | ✅* |
| Eliminar | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Usuarios** |
| Listar todos | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear usuario | ✅ | ✅ | ❌ | ❌ | ❌ |
| Editar usuario | ✅ | ✅ | ❌ | ❌ | ❌ |
| Eliminar usuario | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver perfil propio | ✅ | ✅ | ✅ | ✅ | ✅ |
| Editar perfil propio | ✅ | ✅ | ✅ | ✅ | ✅ |

*Solo en casos asignados/propios

### Principios de Seguridad Implementados

1. **Deny-by-Default**: Sin permiso explícito = acceso denegado
2. **Least Privilege**: Mínimos permisos necesarios por rol
3. **Defense in Depth**: Múltiples capas de validación
4. **Audit Trail**: Logging completo de acciones sensibles
5. **Data Isolation**: Aislamiento completo entre usuarios

## 🛡️ Tests de Seguridad Específicos

### Prevención de Ataques
- ✅ SQL Injection (parametrized queries)
- ✅ XSS (input sanitization)
- ✅ CSRF (token validation)
- ✅ Command Injection (input validation)
- ✅ Path Traversal (file path validation)

### Escalada de Privilegios
- ✅ Horizontal: Usuario A no accede a datos de Usuario B
- ✅ Vertical: Usuario no puede cambiar su propio rol
- ✅ Cross-tenant: Aislamiento completo de datos

### Validación de Inputs
- ✅ Tipos de archivo permitidos
- ✅ Tamaño máximo de archivos (50MB)
- ✅ Formatos de datos
- ✅ Límites de caracteres

## 📊 Métricas de Calidad

### Objetivos de Cobertura
```
Lines covered:    ≥95%
Branches covered: ≥90%
Functions covered: ≥95%
```

### Tipos de Tests
- Unit Tests: ~250 tests
- Integration Tests: ~50 tests
- API Tests: ~150 tests
- Security Tests: ~80 tests
- **Total: ~530+ tests**

## 🔍 Marcadores de Tests

```python
@pytest.mark.unit          # Test unitario
@pytest.mark.integration   # Test de integración
@pytest.mark.api           # Test de API
@pytest.mark.security      # Test de seguridad
@pytest.mark.rbac          # Test RBAC específico
@pytest.mark.performance   # Test de performance
@pytest.mark.slow          # Test lento (>1s)
@pytest.mark.smoke         # Test de smoke (crítico)
```

## 🐛 Debugging Tests

### Ver Output Detallado
```bash
pytest -v -s tests/unit/test_auth.py
```

### Ejecutar Test Específico
```bash
pytest tests/api/test_api_cases_rbac.py::TestCasesAPIAdmin::test_admin_can_create_case -v
```

### Debug con PDB
```bash
pytest --pdb tests/security/test_security.py
```

## 📈 CI/CD Integration

Los tests están diseñados para ejecutarse en:
- GitHub Actions (pipeline automático)
- Pre-commit hooks (validación local)
- Deployment gates (requisito para producción)

### Criterios de Aceptación
- ✅ Todos los tests deben pasar
- ✅ Coverage ≥95%
- ✅ Sin errores de linting
- ✅ Sin vulnerabilidades de seguridad

## 🔄 Mantenimiento

### Actualizar Fixtures
Editar `conftest.py` para agregar nuevos fixtures compartidos.

### Agregar Nuevos Tests
1. Crear archivo en el directorio apropiado
2. Usar marcadores apropiados (`@pytest.mark.api`, etc.)
3. Reutilizar fixtures existentes
4. Mantener convención de nombres: `test_<funcionalidad>.py`

### Coverage Incremental
```bash
# Ver qué falta cubrir
pytest --cov=app --cov-report=term-missing tests/

# Generar reporte HTML
pytest --cov=app --cov-report=html tests/
```

## 🎓 Best Practices

1. **Arrange-Act-Assert**: Estructura clara de tests
2. **Fixtures Reutilizables**: Evitar duplicación
3. **Nombres Descriptivos**: `test_admin_can_delete_case`
4. **Tests Aislados**: Sin dependencias entre tests
5. **Mock Servicios Externos**: Redis, Elasticsearch, HSM
6. **Validar Errores**: No solo happy paths

## 📝 Notas Gubernamentales

Este sistema está diseñado para cumplir con:
- Ley marroquí de protección de datos
- Estándares de seguridad gubernamental
- Requisitos de auditoría legal
- Compliance local e internacional

---

**Última actualización**: Octubre 2025
**Mantenido por**: Equipo de Desarrollo Sistema Judicial Digital
