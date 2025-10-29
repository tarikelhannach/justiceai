# backend/app/routes/search.py - Endpoints de búsqueda con Elasticsearch

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..auth.jwt import get_current_user
from ..models import User
from ..services.elasticsearch_service import get_elasticsearch_service

router = APIRouter(prefix="/api/search", tags=["search"])

class SearchResult(BaseModel):
    id: int
    type: str  # 'document' or 'case'
    title: str
    snippet: str
    score: float
    highlights: Optional[dict] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]

@router.get("/documents", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=2, description="Texto de búsqueda"),
    case_id: Optional[int] = Query(None, description="Filtrar por caso"),
    language: Optional[str] = Query(None, description="Filtrar por idioma (ar, fr, es)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Buscar documentos por texto completo usando Elasticsearch.
    Soporta búsqueda multi-idioma (árabe, francés, español).
    """
    try:
        es_service = get_elasticsearch_service()
        
        if not es_service.connected:
            # Fallback a búsqueda SQL si Elasticsearch no está disponible
            raise HTTPException(
                status_code=503,
                detail="Servicio de búsqueda no disponible. Use /api/documents/ para listar documentos."
            )
        
        results = es_service.search_documents(
            query=q,
            case_id=case_id,
            language=language,
            limit=limit
        )
        
        search_results = []
        for result in results:
            # Crear snippet del texto OCR
            ocr_text = result.get('ocr_text', '')
            snippet = ocr_text[:200] + '...' if len(ocr_text) > 200 else ocr_text
            
            search_results.append(SearchResult(
                id=result['document_id'],
                type='document',
                title=result.get('filename', 'Sin título'),
                snippet=snippet,
                score=result.get('score', 0),
                highlights=result.get('highlights')
            ))
        
        return SearchResponse(
            query=q,
            total_results=len(search_results),
            results=search_results
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.get("/cases", response_model=SearchResponse)
async def search_cases(
    q: str = Query(..., min_length=2, description="Texto de búsqueda"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Buscar casos por texto completo usando Elasticsearch.
    Busca en título, descripción y número de caso.
    """
    try:
        es_service = get_elasticsearch_service()
        
        if not es_service.connected:
            raise HTTPException(
                status_code=503,
                detail="Servicio de búsqueda no disponible. Use /api/cases/ para listar casos."
            )
        
        results = es_service.search_cases(
            query=q,
            status=status,
            limit=limit
        )
        
        search_results = []
        for result in results:
            # Crear snippet de la descripción
            description = result.get('description', '')
            snippet = description[:200] + '...' if len(description) > 200 else description
            
            search_results.append(SearchResult(
                id=result['case_id'],
                type='case',
                title=result.get('title', 'Sin título'),
                snippet=snippet,
                score=result.get('score', 0),
                highlights=result.get('highlights')
            ))
        
        return SearchResponse(
            query=q,
            total_results=len(search_results),
            results=search_results
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.get("/all", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., min_length=2, description="Texto de búsqueda"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Buscar en documentos y casos simultáneamente.
    Retorna resultados combinados ordenados por relevancia.
    """
    try:
        es_service = get_elasticsearch_service()
        
        if not es_service.connected:
            raise HTTPException(
                status_code=503,
                detail="Servicio de búsqueda no disponible"
            )
        
        # Buscar en ambos índices
        doc_results = es_service.search_documents(query=q, limit=limit // 2)
        case_results = es_service.search_cases(query=q, limit=limit // 2)
        
        search_results = []
        
        # Agregar resultados de documentos
        for result in doc_results:
            ocr_text = result.get('ocr_text', '')
            snippet = ocr_text[:200] + '...' if len(ocr_text) > 200 else ocr_text
            
            search_results.append(SearchResult(
                id=result['document_id'],
                type='document',
                title=result.get('filename', 'Sin título'),
                snippet=snippet,
                score=result.get('score', 0),
                highlights=result.get('highlights')
            ))
        
        # Agregar resultados de casos
        for result in case_results:
            description = result.get('description', '')
            snippet = description[:200] + '...' if len(description) > 200 else description
            
            search_results.append(SearchResult(
                id=result['case_id'],
                type='case',
                title=result.get('title', 'Sin título'),
                snippet=snippet,
                score=result.get('score', 0),
                highlights=result.get('highlights')
            ))
        
        # Ordenar por score
        search_results.sort(key=lambda x: x.score, reverse=True)
        search_results = search_results[:limit]
        
        return SearchResponse(
            query=q,
            total_results=len(search_results),
            results=search_results
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )
