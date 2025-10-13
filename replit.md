# Sistema Judicial Digital - Marruecos

## Overview
This is a comprehensive judicial system for Morocco, featuring a FastAPI backend and React frontend with Material-UI. The project was designed for government use with features including case management, OCR processing, HSM digital signatures, and audit logging.

## Project Status
- **Frontend**: ✅ Running on port 5000 with React + Vite + Material-UI
- **Backend**: ⚙️ Configured but not running (requires external services)
- **Deployment**: ✅ Configured for Autoscale

## Current State in Replit
The project is currently running in a simplified mode:
- Frontend displays an admin dashboard with demo data
- Backend API endpoints are not yet connected (would require PostgreSQL, Redis, Elasticsearch)
- The frontend works standalone to demonstrate the UI/UX

## Recent Changes (Replit Setup)
- **2025-10-13**: 
  - Installed Python 3.11 and Node.js 20
  - Set up minimal backend dependencies (FastAPI, Uvicorn)
  - Created React frontend with Vite
  - Configured frontend to run on port 5000 with proper host settings
  - Added demo data to AdminDashboard component
  - Created .gitignore for Python and Node.js
  - Configured deployment for Autoscale

## Project Architecture

### Frontend (frontend/)
- **Framework**: React 18 with Vite
- **UI Library**: Material-UI (MUI) v5
- **Port**: 5000 (required for Replit)
- **Host**: 0.0.0.0 (allows Replit proxy)
- **Components**: 
  - AdminDashboard: Main admin interface with stats, activity, and alerts

### Backend (backend/)
- **Framework**: FastAPI
- **Python Version**: 3.11
- **Current Status**: Simplified version with minimal dependencies
- **Port**: 8000 (localhost only)

### Full System Requirements (Not Yet Configured)
The original project requires:
- PostgreSQL 15+ (Database)
- Redis 7+ (Cache & Message Queue)
- Elasticsearch 8.11+ (Search Engine)
- Celery (Async Task Processing)
- Tesseract OCR (Document Processing)
- HSM Integration (Digital Signatures)

## How to Use

### Running Locally
The frontend is automatically started via the configured workflow.

To start the backend manually (requires full dependencies):
```bash
python start_backend.py
```

### Making Changes
- Frontend code is in `frontend/src/`
- Backend code is in `backend/app/`
- The frontend auto-reloads on changes (HMR)

## User Preferences
- Language: Spanish/French/Arabic support planned
- UI Framework: Material-UI preferred
- Demo data currently used for frontend display

## File Structure
```
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.jsx       # Main app component
│   │   └── main.jsx      # Entry point
│   ├── index.html        # HTML template
│   ├── vite.config.js    # Vite configuration
│   └── package.json      # Node dependencies
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py       # Main FastAPI app
│   │   ├── routes/       # API routes
│   │   ├── services/     # Business logic
│   │   └── auth/         # Authentication
│   └── requirements.txt  # Python dependencies
├── start_backend.py      # Backend startup script
└── .gitignore           # Git ignore rules
```

## Deployment
The project is configured for Autoscale deployment:
- Build command: `npm run build --prefix frontend`
- Run command: `npm run preview --prefix frontend -- --host 0.0.0.0 --port 5000`

## Known Limitations in Replit
1. Backend requires external services (PostgreSQL, Redis, Elasticsearch) not available in basic Replit
2. OCR features require Tesseract installation
3. HSM features require hardware/cloud HSM integration
4. Celery workers require Redis broker

## Next Steps
To fully implement the system:
1. Set up Replit PostgreSQL database
2. Configure Redis connection
3. Implement core API endpoints
4. Connect frontend to backend API
5. Add authentication system
6. Implement file upload and OCR processing
