# Sistema Judicial Digital - Marruecos

## Overview
This project is a comprehensive digital judicial system for Morocco, aiming to modernize the country's legal infrastructure. It features a FastAPI backend and a React frontend with Material-UI, designed for government use. Key capabilities include secure case management with JWT authentication, robust role-based access control (RBAC), multi-language support (Spanish, French, Arabic, including RTL), and a modern, intuitive user interface. The system streamlines judicial processes, enhances efficiency, and ensures secure access to legal information, fully compliant with Moroccan legal requirements (Ley 09-08, Ley 53-05). The project is production-ready, with extensive testing, Docker-based deployment, automated backups, and comprehensive documentation.

## User Preferences
- **Languages**: Multi-language support (Spanish, French, Arabic)
- **UI Framework**: Material-UI with modern design
- **Theme**: Dark/Light mode with purple gradient
- **Authentication**: JWT-based with localStorage persistence
- **RTL Support**: Automatic RTL layout for Arabic language
- **Language Persistence**: Selected language stored in localStorage

## System Architecture
The system is built with a decoupled frontend and backend architecture, prioritizing a security-first, scalable, and localized approach.

### UI/UX Decisions
The frontend features a modern, responsive design with a purple gradient theme, glassmorphism effects, and dark/light mode. It includes a responsive sidebar, dynamic content rendering, and role-specific dashboards for Admin, Judge, Lawyer, and Citizen users. Multi-language support with `react-i18next` includes full Right-to-Left (RTL) layout for Arabic.

### Technical Implementations
- **Frontend**: React 18 with Vite, Material-UI (MUI) v5, React Router v6, Axios, and `react-i18next`.
- **Backend**: FastAPI, Python 3.11, SQLAlchemy for ORM, and PostgreSQL.
- **Authentication**: JWT-based using `python-jose` and `passlib[bcrypt]`.
- **Role-Based Access Control (RBAC)**: Implemented on both frontend and backend for granular access based on user roles (Admin, Judge, Lawyer, Clerk, Citizen), including field-level permissions.
- **Case Management**: Provides CRUD operations and advanced search with filters and RBAC.
- **Document Management**: Secure upload/download with RBAC, storing files on the local filesystem.
- **Internationalization**: Dynamic language switching and RTL adjustments for Spanish, French, and Arabic.

### Feature Specifications
- **Authentication**: User login, registration, secure JWT token management with rate limiting, 2FA TOTP support, password reset flow, and "Remember Me" functionality.
- **Two-Factor Authentication (2FA)**: TOTP-based 2FA with QR code generation, mobile app integration (Google Authenticator, Authy), and secure verification flow.
- **Password Reset**: Complete password reset flow with email token generation, secure confirmation, and URL parameter support.
- **Remember Me**: Email persistence in localStorage for improved UX.
- **Case Operations**: Role-specific CRUD and modification rights for cases.
- **Advanced Search**: Backend endpoint for complex queries, integrated with a debounced, auto-completing frontend search bar.
- **Role-Specific Dashboards**: Dynamically routes users to tailored dashboards.
- **Breadcrumb Navigation**: Dynamic breadcrumb navigation based on current route with RTL support and clickable navigation.
- **PrivateRoute Component**: Enhanced route protection with RBAC validation, role-specific access control, and detailed "Access Denied" screens.
- **Audit Dashboard**: Comprehensive audit system with visualization, advanced filtering, pagination, and RBAC (admin/clerk).
- **Audit Logging**: Comprehensive logging of all user actions in PostgreSQL for security and compliance.
- **Rate Limiting**: Implemented with SlowAPI to prevent brute force attacks and spam, with tiered limits.

### System Design Choices
- **Microservices-oriented**: Clear separation between frontend and backend.
- **Scalability**: Configured for Autoscale deployment.
- **Security-first**: Emphasizes JWT, RBAC, field-level permissions, deny-by-default, and rate limiting.
- **Localization**: Robust multi-language and RTL support.

## External Dependencies

### Backend
- **Framework**: `fastapi`, `uvicorn`
- **Database ORM**: `sqlalchemy`
- **Database Driver**: `psycopg2-binary` (PostgreSQL)
- **Authentication**: `python-jose[cryptography]`, `passlib[bcrypt]`, `pyotp`, `qrcode[pil]`
- **File Handling**: `python-multipart`
- **Data Validation**: `pydantic[email]`
- **Rate Limiting**: `slowapi`
- **Caching**: `redis`

### Frontend
- **Framework**: `react`, `react-dom`, `vite`
- **UI Library**: `@mui/material`, `@emotion/react`, `@emotion/styled`, `@mui/icons-material`
- **Routing**: `react-router-dom`
- **HTTP Client**: `axios`
- **Internationalization**: `i18next`, `react-i18next`, `i18next-browser-languagedetector`