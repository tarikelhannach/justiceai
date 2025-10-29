# Code Quality & Linting - Sistema Judicial Digital

## 📋 Overview

Este documento describe las herramientas y procesos de calidad de código para el Sistema Judicial Digital de Marruecos.

## 🛠️ Herramientas Configuradas

### 1. **Black** - Formateo de Código
- Formateo automático y consistente
- Línea máxima: 100 caracteres
- Target: Python 3.11

```bash
# Formatear todo el código
black app/ tests/

# Ver cambios sin aplicar
black --check --diff app/
```

### 2. **isort** - Ordenar Imports
- Organiza imports automáticamente
- Compatible con Black
- Agrupa por: stdlib, third-party, first-party

```bash
# Ordenar imports
isort app/ tests/

# Ver cambios sin aplicar
isort --check-only --diff app/
```

### 3. **Flake8** - Linting
- Detecta errores de estilo y bugs potenciales
- Integrado con docstring checking
- Complejidad ciclomática máxima: 10

```bash
# Ejecutar linting
flake8 app/ tests/
```

### 4. **Mypy** - Type Checking
- Verificación de tipos estática
- Detecta errores de tipo antes de runtime
- Modo estricto para código de producción

```bash
# Type checking
mypy app/
```

### 5. **Bandit** - Security Linting
- Detecta vulnerabilidades de seguridad
- Escanea código en busca de problemas comunes
- Integrado con CI/CD

```bash
# Security scan
bandit -r app/ -c pyproject.toml
```

### 6. **Pre-commit Hooks**
- Ejecuta checks automáticos antes de commit
- Previene commits con código defectuoso
- Incluye todos los linters

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

## 🚀 Scripts de Calidad

### Formatear Código Automáticamente
```bash
./format.sh
```
Este script:
1. Ordena imports con isort
2. Formatea código con Black
3. Verifica con Flake8

### Verificar Calidad (Sin Cambios)
```bash
./lint.sh
```
Este script ejecuta:
1. ✅ Black (check only)
2. ✅ isort (check only)
3. ✅ Flake8
4. ✅ Mypy
5. ✅ Bandit
6. ✅ Pytest (smoke tests)

## 📊 Estándares de Calidad

### Métricas Objetivo
```
Flake8 Score:      0 errores
Mypy Coverage:     ≥90%
Code Coverage:     ≥95%
Security Issues:   0 críticos
Cyclomatic Complexity: ≤10 por función
```

### Reglas de Estilo
- **Línea máxima**: 100 caracteres
- **Docstrings**: Google style
- **Imports**: Agrupados y ordenados
- **Type hints**: Obligatorios en funciones públicas
- **Nombres**: snake_case para funciones/variables, PascalCase para clases

## 🔒 Reglas de Seguridad (Bandit)

### Checks Activos
- ✅ Hardcoded passwords
- ✅ SQL injection risks
- ✅ Insecure cryptography
- ✅ Unsafe YAML/pickle loads
- ✅ Shell injection
- ✅ XXE vulnerabilities

### Excepciones Permitidas
- B101: assert_used (permitido en tests)
- B601: paramiko_calls (uso controlado)

## 🎯 Workflow de Desarrollo

### 1. Antes de Comenzar
```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### 2. Durante el Desarrollo
```bash
# Formatear código frecuentemente
./format.sh

# Verificar calidad localmente
./lint.sh
```

### 3. Antes de Commit
```bash
# Pre-commit hooks se ejecutan automáticamente
git commit -m "feat: nueva funcionalidad"

# O ejecutar manualmente
pre-commit run --all-files
```

### 4. Antes de PR
```bash
# Ejecutar suite completa
./lint.sh
pytest tests/ --cov=app --cov-report=html

# Verificar coverage
open htmlcov/index.html
```

## 🔧 Configuración

### pyproject.toml
Configuración central para:
- Black
- isort
- Mypy
- Pytest
- Coverage
- Bandit

### .flake8
Configuración específica de Flake8:
- Ignores compatibles con Black
- Complejidad máxima
- Exclusiones de archivos

### .pre-commit-config.yaml
Hooks automáticos:
- Formateo (Black, isort)
- Linting (Flake8, Mypy)
- Security (Bandit)
- Tests (Pytest smoke)

## 🐛 Solución de Problemas

### Error: "Black would reformat X files"
```bash
# Formatear automáticamente
black app/ tests/
```

### Error: "Import X is not sorted"
```bash
# Ordenar imports
isort app/ tests/
```

### Error: "Unused import"
```bash
# Verificar y eliminar imports no usados
# O usar en __init__.py: # noqa: F401
```

### Error: "Type checking failed"
```bash
# Agregar type hints
def function(param: str) -> int:
    return len(param)
```

### Error: "Security issue B201"
```bash
# Revisar uso de Flask o similar
# Usar context managers adecuados
```

## 📈 CI/CD Integration

### GitHub Actions
```yaml
- name: Lint
  run: |
    pip install -r requirements-dev.txt
    ./lint.sh

- name: Type Check
  run: mypy app/

- name: Security Scan
  run: bandit -r app/ -c pyproject.toml

- name: Tests
  run: pytest tests/ --cov=app --cov-fail-under=95
```

### Pre-deployment Checks
✅ Todos los tests pasan
✅ Coverage ≥95%
✅ Sin errores de linting
✅ Sin issues de seguridad
✅ Type checking OK

## 📝 Best Practices

1. **Commit Frecuente**: Pre-commit hooks detectan problemas temprano
2. **Format Before Review**: Código formateado es más fácil de revisar
3. **Type Hints**: Mejoran documentación y detectan errores
4. **Security First**: Bandit debe ejecutarse antes de deployment
5. **Coverage Matters**: Mantener ≥95% en código de producción

## 🎓 Referencias

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

**Última actualización**: Octubre 2025
**Mantenido por**: Equipo de Desarrollo Sistema Judicial Digital
