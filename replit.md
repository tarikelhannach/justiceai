# Sistema Judicial Digital - Marruecos

## Overview
This project is a comprehensive digital judicial system for Morocco, aiming to modernize the country's legal infrastructure. It features a FastAPI backend and a React frontend with Material-UI, designed for government use. Key capabilities include secure case management with JWT authentication, robust role-based access control (RBAC), multi-language support (Spanish, French, Arabic, including RTL), and a modern, intuitive user interface. The system streamlines judicial processes, enhances efficiency, and ensures secure access to legal information.

## User Preferences
- **Languages**: Multi-language support (Spanish, French, Arabic)
- **UI Framework**: Material-UI with modern design
- **Theme**: Dark/Light mode with purple gradient
- **Authentication**: JWT-based with localStorage persistence
- **RTL Support**: Automatic RTL layout for Arabic language
- **Language Persistence**: Selected language stored in localStorage

## System Architecture
The system is built with a decoupled frontend and backend architecture.

### UI/UX Decisions
The frontend prioritizes a modern, responsive user experience with:
- A purple gradient theme featuring glassmorphism effects.
- Dark/light mode toggle with persistence.
- Responsive sidebar navigation and dynamic content rendering.
- Role-specific dashboards provide tailored experiences for Admin, Judge, Lawyer, and Citizen users.
- Multi-language support with `react-i18next`, including full Right-to-Left (RTL) layout for Arabic.

### Technical Implementations
- **Frontend**: Developed using React 18 with Vite, Material-UI (MUI) v5 for UI components, React Router v6 for navigation, Axios for API communication, and `react-i18next` for internationalization.
- **Backend**: Implemented with FastAPI, Python 3.11, SQLAlchemy for ORM, and PostgreSQL as the primary database.
- **Authentication**: JWT-based authentication with `python-jose` and `passlib[bcrypt]` for secure password hashing.
- **Role-Based Access Control (RBAC)**: Implemented on both frontend (`usePermissions` hook) and backend, ensuring granular access to features and data based on user roles (Admin, Judge, Lawyer, Clerk, Citizen). This includes field-level permissions and automatic filtering of data.
- **Case Management**: Provides CRUD operations for cases, including advanced search functionalities with filters and RBAC.
- **Document Management**: Supports secure document upload and download with RBAC validation, utilizing the local filesystem for storage.
- **Internationalization**: Comprehensive support for Spanish, French, and Arabic, with dynamic language switching and RTL layout adjustments.

### Feature Specifications
- **Authentication**: User login, registration, and secure JWT token management with rate limiting (5 login attempts/minute, 3 registrations/hour per IP).
- **Case Operations**: Create, read, update, delete cases, with role-specific access and modification rights.
- **Advanced Search**: Backend endpoint supporting complex queries across various case attributes, integrated with a debounced, auto-completing search bar on the frontend.
- **Role-Specific Dashboards**: Dynamically routes users to tailored dashboards based on their assigned role, displaying only relevant information and actions.
- **Audit Dashboard**: Complete audit system with visualization (Recharts), advanced filtering, pagination with AbortController to prevent race conditions, and RBAC (admin/clerk access). Includes stats, action types, resource types, and comprehensive log search.
- **Audit Logging**: Comprehensive logging of all user actions for security and compliance, with structured storage in PostgreSQL.
- **Rate Limiting**: Comprehensive rate limiting using SlowAPI to prevent brute force attacks and spam, with tiered limits for different endpoints and user types.

### System Design Choices
- **Microservices-oriented**: Clear separation between frontend and backend.
- **Scalability**: Configured for Autoscale deployment.
- **Security-first**: Emphasizes JWT, RBAC, field-level permissions, deny-by-default policies, and rate limiting.
- **Localization**: Designed for international use with robust multi-language and RTL support.

## Security Features (Production Ready)

### Rate Limiting & DDoS Protection
- **Implementation**: SlowAPI (0.1.9) with in-memory storage (production uses Redis)
- **Login Protection**: 5 attempts/minute per IP (brute force prevention)
- **Registration Protection**: 3 attempts/hour per IP (spam prevention)
- **API Rate Limits**: 
  - Authenticated users: 100 requests/minute per user
  - Anonymous users: 20 requests/minute per IP
- **Response Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **Proxy Support**: Handles X-Forwarded-For and X-Real-IP headers correctly

### Rate Limit Configuration
```python
# Login endpoint
@ip_limiter.limit("5/minute")  # By IP
async def login(...)

# Register endpoint  
@ip_limiter.limit("3/hour")  # By IP

# API endpoints
@user_limiter.limit("100/minute")  # By user/IP
async def api_endpoint(...)
```

## Testing Infrastructure (Production Ready)

### Test Organization
- **Unit Tests**: `backend/tests/unit/` - Tests aislados de módulos
- **Integration Tests**: `backend/tests/integration/` - Tests con servicios externos
- **Security Tests**: `backend/tests/security/` - XSS, CSRF, SQL injection
- **API Tests**: `backend/tests/api/` - Endpoints con todos los roles
- **Performance Tests**: `backend/tests/performance/` - Carga y concurrencia

### Test Fixtures
Complete fixtures for all government roles:
- **admin_user / admin_token / admin_headers** - Administrador
- **judge_user / judge_token / judge_headers** - Juez
- **lawyer_user / lawyer_token / lawyer_headers** - Abogado
- **clerk_user / clerk_token / clerk_headers** - Secretario Judicial
- **citizen_user / citizen_token / citizen_headers** - Ciudadano

### Test Execution
- **Run all tests**: `cd backend && ./run_tests.sh all`
- **Unit tests only**: `./run_tests.sh unit`
- **Security tests**: `./run_tests.sh security`
- **Coverage report**: `./run_tests.sh coverage` (HTML: htmlcov/index.html)
- **Target coverage**: ≥95% for production readiness

### Mock Services
- **Redis**: mock_redis fixture for caching
- **Elasticsearch**: mock_elasticsearch for search
- **HSM**: mock_hsm for digital signatures

## Code Quality & Standards

### Linting Tools (Production Ready)
- **Black**: Code formatter with line-length 100
- **isort**: Import sorting compatible with Black
- **Flake8**: Style guide enforcement (E501, W503 ignored for Black compatibility)
- **mypy**: Static type checking with strict mode
- **Bandit**: Security vulnerability scanning
- **pre-commit**: Automated hooks for all linters

### Quality Commands
- **Format code**: `cd backend && black . && isort .`
- **Check style**: `flake8 .`
- **Type check**: `mypy app/`
- **Security scan**: `bandit -r app/`
- **Pre-commit setup**: `pre-commit install && pre-commit run --all-files`
- **Full quality check**: `./check_quality.sh` (runs all tools)

### Standards
- Line length: 100 characters
- Type hints: Required for all functions
- Docstrings: Google style for public APIs
- Security: No hardcoded secrets, SQL injection prevention

## External Dependencies

### Backend
- **Framework**: `fastapi`, `uvicorn`
- **Database ORM**: `sqlalchemy`
- **Database Driver**: `psycopg2-binary` (PostgreSQL)
- **Authentication**: `python-jose[cryptography]`, `passlib[bcrypt]`
- **File Handling**: `python-multipart`
- **Data Validation**: `pydantic[email]`
- **Testing**: `pytest`, `pytest-asyncio`, `pytest-cov`, `factory-boy`, `faker`

### Frontend
- **Framework**: `react`, `react-dom`, `vite`
- **UI Library**: `@mui/material`, `@emotion/react`, `@emotion/styled`, `@mui/icons-material`
- **Routing**: `react-router-dom`
- **HTTP Client**: `axios`
- **Internationalization**: `i18next`, `react-i18next`, `i18next-browser-languagedetector`