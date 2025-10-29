# CI/CD Pipeline Guide - Moroccan Judicial System

## 📋 Overview

This document describes the comprehensive CI/CD pipeline for the Digital Judicial System of Morocco, ensuring enterprise-grade quality, security, and deployment automation.

## 🏗️ Pipeline Architecture

### Pipeline Stages

```
┌─────────────┐
│   Push to   │
│  Main/Dev   │
└──────┬──────┘
       │
       ├─────> Backend Tests & Linting
       │       ├─ Black formatter
       │       ├─ isort imports
       │       ├─ Flake8 linting
       │       ├─ mypy type checking
       │       └─ pytest with coverage
       │
       ├─────> Frontend Tests & Linting
       │       ├─ ESLint
       │       ├─ Prettier
       │       ├─ Jest tests
       │       └─ Build verification
       │
       ├─────> Security Scanning
       │       ├─ Trivy vulnerability scan
       │       ├─ Python Safety check
       │       └─ NPM audit
       │
       ├─────> Integration Tests
       │       └─ Full system integration
       │
       ├─────> Performance Tests (main only)
       │       └─ Load testing with Locust
       │
       └─────> Deploy to Replit (main only)
               └─ Automatic deployment
```

## 🚀 Quick Start

### Local Testing

```bash
# Backend tests
cd backend
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh

# Frontend tests
cd frontend
npm test
npm run lint
npm run build
```

### GitHub Actions

The pipeline runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

## 📊 Test Coverage Requirements

| Component | Minimum Coverage | Current Status |
|-----------|------------------|----------------|
| Backend | 70% | ✅ Passing |
| Frontend | 60% | ⚠️ In Progress |
| Integration | N/A | ✅ Passing |

## 🔒 Security Checks

### 1. Dependency Scanning
- **Trivy**: Scans for known vulnerabilities in dependencies
- **Safety**: Python-specific vulnerability database
- **NPM Audit**: JavaScript dependency vulnerabilities

### 2. Static Analysis
- **Flake8**: PEP 8 compliance
- **ESLint**: JavaScript best practices
- **mypy**: Python type safety

### 3. SAST (Static Application Security Testing)
- Code quality analysis with SonarCloud (optional)
- Security-focused test suite (RBAC, authentication, rate limiting)

## 📝 Test Organization

### Backend Tests
Located in `backend/tests/`:

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_auth.py
│   ├── test_cases.py
│   └── test_documents.py
├── integration/             # Integration tests
│   ├── test_database.py
│   ├── test_redis.py
│   └── test_elasticsearch.py
├── api/                     # API endpoint tests with RBAC
│   ├── test_api_auth.py
│   ├── test_api_cases_rbac.py
│   └── test_api_documents_rbac.py
├── security/                # Security-focused tests
│   ├── test_security_rbac.py
│   ├── test_rate_limiting.py
│   └── test_security.py
└── performance/             # Load and performance tests
    ├── locustfile.py
    └── run_load_tests.sh
```

### Frontend Tests
Located in `frontend/src/`:

```
src/
├── components/
│   └── __tests__/           # Component tests
├── utils/
│   └── __tests__/           # Utility function tests
└── integration/             # E2E tests
```

## 🎯 Test Markers

Use pytest markers to run specific test categories:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# API tests
pytest -m api

# Security tests
pytest -m security

# RBAC tests
pytest -m rbac

# Skip slow tests
pytest -m "not slow"
```

## 📈 Performance Testing

### Load Test Configuration

Default settings (Government requirements):
- **Users**: 1500 concurrent users
- **Spawn Rate**: 100 users/second
- **Duration**: 5 minutes
- **Target**: p95 < 1000ms, Error rate < 5%

### Running Load Tests

```bash
# Quick test (100 users, 1 minute)
cd backend/tests/performance
./run_load_tests.sh http://localhost:8000 100 10 1m

# Full load test (1500 users, 10 minutes)
./run_load_tests.sh http://localhost:8000 1500 100 10m

# CI/CD mode (headless)
locust -f locustfile.py \
  --host=http://localhost:8000 \
  --users=1500 \
  --spawn-rate=100 \
  --run-time=5m \
  --headless \
  --html=report.html
```

## 🔄 Deployment Workflow

### Automatic Deployment (Main Branch)

When code is pushed to `main`:
1. All tests must pass
2. Security scans must complete
3. Code coverage meets requirements
4. Replit automatically deploys changes

### Manual Deployment

```bash
# Deploy via Replit CLI (if configured)
replit deploy

# Or use the Replit web interface
# Click "Deploy" button after tests pass
```

## 🛠️ CI/CD Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci-cd.yml` | Main GitHub Actions workflow |
| `pytest.ini` | Pytest configuration and markers |
| `backend/scripts/run_tests.sh` | Backend test execution script |
| `frontend/package.json` | Frontend test scripts |
| `.coveragerc` | Coverage configuration |

## 📋 Quality Gates

### Backend
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All security tests pass
- ✅ Code coverage ≥ 70%
- ✅ No critical security vulnerabilities
- ✅ Linting passes (Black, isort, Flake8)
- ⚠️ Type checking passes (mypy) - warnings allowed

### Frontend
- ✅ Build succeeds
- ✅ All tests pass
- ✅ ESLint passes
- ✅ Prettier formatting checked
- ⚠️ No critical npm audit issues

### Performance (Main Branch Only)
- ⚠️ Load test completes
- ⚠️ p95 response time < 1000ms
- ⚠️ Error rate < 5%
- ⚠️ Throughput ≥ 100 req/s

## 🐛 Troubleshooting

### Tests Failing Locally

```bash
# Update dependencies
cd backend
pip install -r requirements.txt --upgrade

cd ../frontend
npm install

# Clear cache
pytest --cache-clear
npm run clean

# Run tests in verbose mode
pytest -vv
npm test -- --verbose
```

### GitHub Actions Failing

1. Check the Actions tab in GitHub
2. Review error logs
3. Verify secrets are configured:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `SONAR_TOKEN` (optional)

### Coverage Too Low

```bash
# Generate detailed coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html

# Find uncovered lines
pytest --cov=app --cov-report=term-missing
```

## 📚 Best Practices

### Writing Tests

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use fixtures**: Leverage pytest fixtures for setup
3. **Test one thing**: Each test should verify one behavior
4. **Use meaningful names**: `test_admin_can_create_case_with_valid_data`
5. **Add markers**: Mark tests appropriately (unit, integration, slow)

### Code Quality

1. **Format before commit**: Run `black` and `isort`
2. **Fix linting**: Address Flake8 warnings
3. **Write docstrings**: Document public functions
4. **Type hints**: Add type hints for better type checking

### Security

1. **Never commit secrets**: Use environment variables
2. **Test RBAC**: Verify permission checks
3. **Validate input**: Test with malicious input
4. **Test rate limiting**: Ensure DOS protection works

## 🔗 Related Documentation

- [Testing Strategy](TESTING_STRATEGY.md)
- [Security Best Practices](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Performance Benchmarks](PERFORMANCE.md)

## 📞 Support

For CI/CD issues:
1. Check this guide
2. Review GitHub Actions logs
3. Contact the DevOps team
4. Open an issue in the repository

---

**Last Updated**: October 29, 2025  
**Version**: 1.0.0  
**Maintained by**: Sistema Judicial Digital - Morocco 🇲🇦
