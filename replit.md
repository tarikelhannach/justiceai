# Sistema Judicial Digital - Marruecos

## Overview
This is a comprehensive judicial system for Morocco, featuring a FastAPI backend and React frontend with Material-UI. The project includes case management, modern UI/UX, JWT authentication, and role-based access control for government use.

## Project Status
- **Frontend**: ✅ Running on port 5000 with React + Vite + Material-UI + React Router
- **Backend**: ✅ Running on port 8000 with FastAPI + PostgreSQL + JWT Auth
- **Database**: ✅ PostgreSQL configured with demo data
- **Authentication**: ✅ JWT-based auth with login/register fully functional
- **Deployment**: ✅ Configured for Autoscale

## Current State - MVP Functional
The MVP is now functional with:
- ✅ Modern UI with dark/light theme, gradient design, glassmorphism effects
- ✅ Complete authentication system (login/register/logout)
- ✅ Secure REST API with role-based access control (RBAC)
- ✅ Case management CRUD operations
- ✅ PostgreSQL database with User, Case, Document, AuditLog models
- ✅ Demo data populated (4 users, 3 cases)
- ✅ Protected routes and authorization

## Recent Changes (October 13, 2025)

### Backend Implementation ✅
- **Database Setup**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based auth with password hashing (bcrypt)
- **API Endpoints**:
  - `/api/auth/login` - User login with JWT token
  - `/api/auth/register` - User registration
  - `/api/auth/me` - Get current user info
  - `/api/auth/logout` - Logout and audit logging
  - `/api/cases/` - CRUD operations for cases with RBAC
  - `/api/cases/{id}` - Get/update/delete specific case
  - `/api/cases/stats/summary` - Case statistics
- **Security**: 
  - Field-level permissions (citizens/lawyers cannot modify status or judge assignment)
  - Role-based access control for all operations
  - Judge assignment validation
  - Deny-by-default for unknown roles
  - Audit logging for all actions

### Frontend Implementation ✅
- **Modern UI Design**: 
  - Purple gradient theme with glassmorphism
  - Dark/light mode toggle with localStorage persistence
  - Responsive sidebar navigation
  - Modern cards, buttons, and animations
- **Authentication UI**:
  - Beautiful login/register form with tabs
  - Form validation (password confirmation, length, required fields)
  - Error handling with Spanish messages
  - Demo user credentials displayed
- **State Management**:
  - AuthContext for authentication state
  - Token persistence in localStorage
  - Protected routes with redirect
  - Automatic 401 handling
- **API Integration**:
  - Axios service with interceptors
  - Bearer token authentication
  - Error handling
- **Dashboard Features**:
  - Real-time case statistics from backend API
  - Auto-refresh every 30 seconds
  - Recent cases display with status, owner, and judge info
  - Error handling with dismissible alerts
  - Loading states and graceful fallbacks

## Demo Users
Access the system with these credentials:
- **Admin**: `admin@justicia.ma` / `admin123`
- **Judge**: `juez@justicia.ma` / `juez123`
- **Lawyer**: `abogado@justicia.ma` / `abogado123`
- **Clerk**: `secretario@justicia.ma` / `secretario123`

## Project Architecture

### Frontend (frontend/)
- **Framework**: React 18 with Vite
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Port**: 5000 (required for Replit)
- **Host**: 0.0.0.0 (allows Replit proxy)
- **Components**: 
  - `Login.jsx`: Modern login/register form
  - `Layout.jsx`: Sidebar navigation with user info
  - `AdminDashboard.jsx`: Main dashboard with stats
  - `AuthContext`: Authentication state management
  - `api.js`: Axios API service

### Backend (backend/)
- **Framework**: FastAPI
- **Python Version**: 3.11
- **Database**: PostgreSQL (Replit hosted)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Port**: 8000
- **File Storage**: Local filesystem (/tmp/judicial_documents)
- **Models**:
  - `User`: Email, password, role (admin/judge/lawyer/clerk/citizen)
  - `Case`: Case number, title, description, status, owner, assigned judge
  - `Document`: File metadata, file path, size, mime type
  - `AuditLog`: Complete audit trail of all actions
- **Routes**:
  - `auth.py`: Authentication endpoints
  - `cases.py`: Case management with RBAC
  - `documents.py`: Document upload/download with RBAC

### Database Schema
```
Users
  - id, email, name, hashed_password, role, is_active, is_verified

Cases
  - id, case_number, title, description, status, owner_id, assigned_judge_id
  - Relationships: owner (User), assigned_judge (User), documents

Documents
  - id, filename, file_path, case_id, uploaded_by, ocr_text, is_signed

AuditLogs
  - id, user_id, action, resource_type, resource_id, ip_address, status
```

## Role-Based Access Control (RBAC)

### Permissions by Role:
- **Admin & Clerk**: Full access to all cases and all fields
- **Judge**: Access to assigned cases, can modify status and details
- **Lawyer**: Access to owned cases, can modify title/description only
- **Citizen**: Access to owned cases, can modify title/description only

### Security Features:
- Field-level permissions prevent privilege escalation
- Judge assignment validation (must be actual judge role)
- Deny-by-default for unknown roles
- Complete audit logging of all actions

## How to Use

### Running the Application
Both frontend and backend are automatically started via configured workflows:
- Frontend: `http://localhost:5000` (or Replit URL)
- Backend API: `http://localhost:8000/api`
- API Docs: `http://localhost:8000/docs` (when debug=true)

### Making Changes
- Frontend code: `frontend/src/`
- Backend code: `backend/app/`
- Database models: `backend/app/models.py`
- API routes: `backend/app/routes/`
- Auto-reload enabled on both services (HMR)

### Database Management
- Initialize DB: `python backend/init_db.py`
- Models are in: `backend/app/models.py`
- The database is automatically created on first run

## File Structure
```
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Login.jsx    # Auth UI
│   │   │   ├── Layout.jsx   # Sidebar layout
│   │   │   └── AdminDashboard.jsx
│   │   ├── context/         # React contexts
│   │   │   └── AuthContext.jsx
│   │   ├── services/        # API services
│   │   │   └── api.js       # Axios client
│   │   ├── App.jsx          # Main app with routing
│   │   ├── main.jsx         # Entry point
│   │   └── theme.js         # MUI theme config
│   ├── vite.config.js       # Vite config (host: 0.0.0.0)
│   └── package.json         # Dependencies
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database.py      # DB connection
│   │   ├── config.py        # Settings
│   │   ├── routes/          # API routes
│   │   │   ├── auth.py      # Authentication
│   │   │   └── cases.py     # Case management
│   │   └── auth/            # Auth utilities
│   │       └── jwt.py       # JWT functions
│   ├── init_db.py           # Database initialization
│   └── requirements.txt     # Dependencies
└── .gitignore              # Git ignore rules
```

## Deployment
The project is configured for Autoscale deployment:
- Build command: `npm run build --prefix frontend`
- Run command: `npm run preview --prefix frontend -- --host 0.0.0.0 --port 5000`

## Dependencies

### Backend
- fastapi
- uvicorn
- sqlalchemy
- psycopg2-binary
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart
- pydantic[email]

### Frontend
- react
- react-dom
- react-router-dom
- @mui/material
- @emotion/react
- @emotion/styled
- @mui/icons-material
- axios

## Next Steps for Full System

### Immediate (MVP Complete)
1. ✅ JWT Authentication
2. ✅ Case Management API
3. ✅ Modern UI/UX
4. ✅ Role-Based Access Control

### Phase 2 (Document Management) ✅ COMPLETED
1. ✅ Document upload API endpoint with RBAC
2. ✅ File storage integration (filesystem-based)
3. ✅ Document upload component with drag-and-drop UI
4. ✅ File download functionality with permissions
5. ✅ Secure file management (50MB limit, type validation)

### Phase 3 (Advanced Features)
1. OCR processing (Tesseract integration)
2. Search functionality
3. Notifications system
4. Multi-language support (AR/FR/ES)
5. Analytics and reporting

### Future Enhancements
1. Real-time updates (WebSockets)
2. HSM digital signatures
3. Elasticsearch for advanced search
4. Redis for caching
5. Celery for async tasks

## Known Limitations
1. Document upload not yet implemented (Phase 2)
2. OCR features require Tesseract installation
3. HSM features require hardware/cloud HSM integration
4. Search limited to basic database queries

## User Preferences
- **Language**: Spanish (ES) used for UI messages
- **UI Framework**: Material-UI with modern design
- **Theme**: Dark/Light mode with purple gradient
- **Authentication**: JWT-based with localStorage persistence
