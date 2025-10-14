from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import io
import shutil
from pathlib import Path
import uuid

from ..database import get_db
from ..models import Document as DocumentModel, User, Case
from ..auth.jwt import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    case_id: Optional[int]
    uploaded_by: int
    ocr_processed: bool
    is_signed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    message: str

UPLOAD_DIR = Path("/tmp/judicial_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

MAX_FILE_SIZE = 50 * 1024 * 1024

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if case_id:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caso no encontrado"
            )
        
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="No autorizado para subir documentos a este caso"
                    )
            elif case.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No autorizado para subir documentos a este caso"
                )
    
    if not file.content_type in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Tipos aceptados: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    file_path = None
    try:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        user_dir = UPLOAD_DIR / str(current_user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = user_dir / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        new_document = DocumentModel(
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=file.content_type,
            case_id=case_id,
            uploaded_by=current_user.id
        )
        
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
        
        try:
            from app.tasks.ocr_tasks import process_document_ocr, index_document_elasticsearch
            from celery import chord
            
            workflow = chord([process_document_ocr.s(new_document.id)], 
                           index_document_elasticsearch.s())
            result = workflow.apply_async()
            
            message = f"Documento subido exitosamente. OCR en proceso (task_id: {result.id})"
        except Exception as e:
            message = f"Documento subido exitosamente. OCR no disponible: {str(e)}"
        
        return DocumentUploadResponse(
            id=new_document.id,
            filename=new_document.filename,
            file_path=new_document.file_path,
            message=message
        )
    
    except Exception as e:
        db.rollback()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir documento: {str(e)}"
        )

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    if document.case_id:
        case = db.query(Case).filter(Case.id == document.case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Caso asociado no encontrado")
        
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado para acceder a este documento")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado para acceder a este documento")
    
    elif document.uploaded_by != current_user.id and current_user.role.value not in ["admin", "clerk"]:
        raise HTTPException(status_code=403, detail="No autorizado para acceder a este documento")
    
    try:
        file_path = Path(document.file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado en el servidor"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type=document.mime_type or "application/octet-stream",
            filename=document.filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar documento: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    case_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DocumentModel)
    
    if case_id:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Caso no encontrado")
        
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado")
        
        query = query.filter(DocumentModel.case_id == case_id)
    else:
        if current_user.role.value not in ["admin", "clerk"]:
            query = query.filter(DocumentModel.uploaded_by == current_user.id)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if document.case_id:
        case = db.query(Case).filter(Case.id == document.case_id).first()
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado")
    
    elif document.uploaded_by != current_user.id and current_user.role.value not in ["admin", "clerk"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.core.cache import get_cache_manager
    cache = get_cache_manager()
    
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if current_user.role.value not in ["admin", "clerk"]:
        if document.case_id:
            case = db.query(Case).filter(Case.id == document.case_id).first()
            if not case:
                raise HTTPException(status_code=404, detail="Caso asociado no encontrado")
            
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado para eliminar este documento")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado para eliminar este documento")
        elif document.uploaded_by != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este documento")
    
    try:
        case_id = document.case_id
        
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        
        db.delete(document)
        db.commit()
        
        await cache.invalidate_document(document_id, case_id)
        
        return {"message": "Documento eliminado exitosamente"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar documento: {str(e)}"
        )

@router.post("/{document_id}/process-ocr")
async def process_document_ocr_sync(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Procesar OCR para un documento de forma síncrona.
    Endpoint útil para testing y procesamiento inmediato de documentos pequeños.
    """
    from app.services.ocr_service import SyncOCRService
    
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if document.case_id:
        case = db.query(Case).filter(Case.id == document.case_id).first()
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado")
    elif document.uploaded_by != current_user.id and current_user.role.value not in ["admin", "clerk"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    if document.ocr_processed:
        return {
            "message": "Documento ya procesado con OCR",
            "ocr_text": document.ocr_text,
            "ocr_confidence": document.ocr_confidence,
            "ocr_language": document.ocr_language
        }
    
    try:
        ocr_service = SyncOCRService()
        result = ocr_service.process_document(document.file_path)
        
        document.ocr_processed = True
        document.ocr_text = result['extracted_text']
        document.ocr_confidence = result['ocr_confidence']
        document.ocr_language = result['detected_language']
        document.is_searchable = True
        
        db.commit()
        db.refresh(document)
        
        return {
            "message": "OCR procesado exitosamente",
            "ocr_text": result['extracted_text'],
            "ocr_confidence": result['ocr_confidence'],
            "ocr_language": result['detected_language'],
            "processing_time": result['processing_time'],
            "pages_processed": result['pages_processed']
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar OCR: {str(e)}"
        )
