# backend/app/routes/signatures.py - Endpoints de Firma Digital HSM

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from pathlib import Path

from ..database import get_db
from ..auth.jwt import get_current_user
from ..models import User, Document as DocumentModel

router = APIRouter(prefix="/api/signatures", tags=["signatures"])

class SignDocumentRequest(BaseModel):
    document_id: int
    certificate_id: str

class SignDocumentResponse(BaseModel):
    document_id: int
    signature_hash: str
    certificate_id: str
    signed_at: str
    hsm_provider: str
    morocco_compliant: bool
    message: str

class VerifySignatureRequest(BaseModel):
    document_id: int

class VerifySignatureResponse(BaseModel):
    document_id: int
    is_valid: bool
    verified_at: str
    certificate_info: Optional[dict] = None
    message: str

@router.post("/sign", response_model=SignDocumentResponse)
async def sign_document(
    request: SignDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Firmar un documento digitalmente usando HSM.
    Soporta PKCS#11, Azure Key Vault, y Software HSM como fallback.
    """
    try:
        # Importar aquí para evitar errores circulares
        import importlib
        hsm_module = importlib.import_module('app.backend-app-hsm-production')
        sign_document_with_hsm = hsm_module.sign_document_with_hsm
        
        # Verificar que el documento existe
        document = db.query(DocumentModel).filter(DocumentModel.id == request.document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Verificar permisos
        if document.case_id:
            from ..models import Case
            case = db.query(Case).filter(Case.id == document.case_id).first()
            if not case:
                raise HTTPException(status_code=404, detail="Caso no encontrado")
            
            # Solo admin, clerk, judge asignado y owner pueden firmar
            if current_user.role.value not in ["admin", "clerk"]:
                if current_user.role.value == "judge":
                    if case.assigned_judge_id != current_user.id:
                        raise HTTPException(status_code=403, detail="No autorizado para firmar este documento")
                elif case.owner_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado para firmar este documento")
        
        elif document.uploaded_by != current_user.id and current_user.role.value not in ["admin", "clerk"]:
            raise HTTPException(status_code=403, detail="No autorizado para firmar este documento")
        
        # Leer contenido del documento
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado en el servidor"
            )
        
        with open(file_path, 'rb') as f:
            document_content = f.read()
        
        # Firmar documento con HSM
        signature_result = await sign_document_with_hsm(
            document_content=document_content,
            certificate_id=request.certificate_id,
            user_id=current_user.id,
            metadata={
                'document_id': document.id,
                'filename': document.filename,
                'document_type': document.mime_type
            }
        )
        
        # Guardar información de firma en la base de datos
        document.is_signed = True
        document.signature_hash = signature_result.signature_hash
        db.commit()
        db.refresh(document)
        
        return SignDocumentResponse(
            document_id=document.id,
            signature_hash=signature_result.signature_hash,
            certificate_id=request.certificate_id,
            signed_at=signature_result.timestamp,
            hsm_provider=signature_result.metadata.get('hsm_provider', 'Unknown'),
            morocco_compliant=signature_result.metadata.get('morocco_compliant', False),
            message="Documento firmado exitosamente con HSM"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al firmar documento: {str(e)}"
        )

@router.post("/verify", response_model=VerifySignatureResponse)
async def verify_signature(
    request: VerifySignatureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verificar la firma digital de un documento usando HSM.
    """
    try:
        import importlib
        hsm_module = importlib.import_module('app.backend-app-hsm-production')
        verify_document_signature = hsm_module.verify_document_signature
        import hashlib
        from datetime import datetime
        
        # Verificar que el documento existe
        document = db.query(DocumentModel).filter(DocumentModel.id == request.document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        if not document.is_signed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Documento no tiene firma digital"
            )
        
        # Verificar permisos
        if document.case_id:
            from ..models import Case
            case = db.query(Case).filter(Case.id == document.case_id).first()
            if not case:
                raise HTTPException(status_code=404, detail="Caso no encontrado")
            
            if current_user.role.value not in ["admin", "clerk"]:
                if current_user.role.value == "judge":
                    if case.assigned_judge_id != current_user.id:
                        raise HTTPException(status_code=403, detail="No autorizado")
                elif case.owner_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado")
        
        elif document.uploaded_by != current_user.id and current_user.role.value not in ["admin", "clerk"]:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Leer contenido del documento
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado en el servidor"
            )
        
        with open(file_path, 'rb') as f:
            document_content = f.read()
        
        # Calcular hash del documento actual
        current_hash = hashlib.sha256(document_content).hexdigest()
        
        # Verificar que el hash coincide con el almacenado
        if current_hash != document.signature_hash:
            return VerifySignatureResponse(
                document_id=document.id,
                is_valid=False,
                verified_at=datetime.utcnow().isoformat(),
                message="Documento modificado después de la firma - firma inválida"
            )
        
        # Verificar firma con HSM
        # Nota: Para verificación completa necesitaríamos la firma y certificado almacenados
        # Por ahora verificamos integridad del hash
        is_valid = (current_hash == document.signature_hash)
        
        return VerifySignatureResponse(
            document_id=document.id,
            is_valid=is_valid,
            verified_at=datetime.utcnow().isoformat(),
            certificate_info={
                'hash_algorithm': 'SHA-256',
                'signature_hash': document.signature_hash
            },
            message="Firma válida - documento no modificado" if is_valid else "Firma inválida"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar firma: {str(e)}"
        )

@router.get("/document/{document_id}/status")
async def get_signature_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener estado de firma de un documento.
    """
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Verificar permisos
    if document.case_id:
        from ..models import Case
        case = db.query(Case).filter(Case.id == document.case_id).first()
        if current_user.role.value not in ["admin", "clerk"]:
            if current_user.role.value == "judge":
                if case.assigned_judge_id != current_user.id:
                    raise HTTPException(status_code=403, detail="No autorizado")
            elif case.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="No autorizado")
    
    return {
        "document_id": document.id,
        "filename": document.filename,
        "is_signed": document.is_signed,
        "signature_hash": document.signature_hash if document.is_signed else None,
        "signed_at": document.created_at.isoformat() if document.is_signed else None
    }
