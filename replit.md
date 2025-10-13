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
- **Authentication**: User login, registration, and secure JWT token management.
- **Case Operations**: Create, read, update, delete cases, with role-specific access and modification rights.
- **Advanced Search**: Backend endpoint supporting complex queries across various case attributes, integrated with a debounced, auto-completing search bar on the frontend.
- **Role-Specific Dashboards**: Dynamically routes users to tailored dashboards based on their assigned role, displaying only relevant information and actions.
- **Audit Logging**: Comprehensive logging of all user actions for security and compliance.

### System Design Choices
- **Microservices-oriented**: Clear separation between frontend and backend.
- **Scalability**: Configured for Autoscale deployment.
- **Security-first**: Emphasizes JWT, RBAC, field-level permissions, and deny-by-default policies.
- **Localization**: Designed for international use with robust multi-language and RTL support.

## External Dependencies

### Backend
- **Framework**: `fastapi`, `uvicorn`
- **Database ORM**: `sqlalchemy`
- **Database Driver**: `psycopg2-binary` (PostgreSQL)
- **Authentication**: `python-jose[cryptography]`, `passlib[bcrypt]`
- **File Handling**: `python-multipart`
- **Data Validation**: `pydantic[email]`

### Frontend
- **Framework**: `react`, `react-dom`, `vite`
- **UI Library**: `@mui/material`, `@emotion/react`, `@emotion/styled`, `@mui/icons-material`
- **Routing**: `react-router-dom`
- **HTTP Client**: `axios`
- **Internationalization**: `i18next`, `react-i18next`, `i18next-browser-languagedetector`