# backend/app/routes/__init__.py
"""
Routers para el Sistema Judicial Digital
"""

from . import auth, cases, documents, search, audit, hsm

__all__ = ["auth", "cases", "documents", "search", "audit", "hsm"]
