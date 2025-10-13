# backend/app/hsm/hsm_manager_production_ready.py - Sistema HSM Completo para Marruecos

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
import hashlib
import json
import time

from ..config import settings
from ..models import Document, AuditLog
from .base import HSMInterface, HSMException, SignatureResult, CertificateInfo

logger = logging.getLogger(__name__)

class ProductionHSMManager:
    """
    Manager HSM completo para producción en Marruecos
    Soporta múltiples tipos de HSM y failover automático
    """
    
    def __init__(self):
        self.hsm_providers: Dict[str, HSMInterface] = {}
        self.primary_hsm: Optional[HSMInterface] = None
        self.fallback_hsm: Optional[HSMInterface] = None
        self.is_initialized = False
        self.health_status = {}
        self._initialize_hsm_providers()
    
    def _initialize_hsm_providers(self):
        """Inicializar proveedores HSM basado en configuración"""
        try:
            # Proveedor principal basado en configuración
            if settings.hsm_type == "pkcs11":
                from .pkcs11_hsm import PKCS11HSM
                self.primary_hsm = PKCS11HSM()
                self.hsm_providers["pkcs11"] = self.primary_hsm
                logger.info("PKCS#11 HSM inicializado como proveedor principal")
                
            elif settings.hsm_type == "azure_keyvault":
                from .azure_hsm import AzureKeyVaultHSM
                self.primary_hsm = AzureKeyVaultHSM()
                self.hsm_providers["azure"] = self.primary_hsm
                logger.info("Azure Key Vault inicializado como proveedor principal")
                
            else:
                # Software fallback como principal (desarrollo/testing)
                from .software_hsm import SoftwareHSM
                self.primary_hsm = SoftwareHSM()
                self.hsm_providers["software"] = self.primary_hsm
                logger.info("Software HSM inicializado como proveedor principal")
            
            # Siempre tener software HSM como fallback
            if settings.hsm_type != "software_fallback":
                from .software_hsm import SoftwareHSM
                self.fallback_hsm = SoftwareHSM()
                self.hsm_providers["software_fallback"] = self.fallback_hsm
                logger.info("Software HSM configurado como fallback")
            
            self.is_initialized = True
            logger.info("HSM Manager inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando HSM Manager: {e}")
            raise HSMException(f"Failed to initialize HSM Manager: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud de todos los proveedores HSM
        """
        health_results = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "providers": {}
        }
        
        for name, provider in self.hsm_providers.items():
            try:
                provider_health = await provider.health_check()
                health_results["providers"][name] = provider_health
                
                # Actualizar status global
                if provider_health.get("status") != "healthy":
                    health_results["status"] = "degraded"
                    
            except Exception as e:
                health_results["providers"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_results["status"] = "degraded"
        
        self.health_status = health_results
        return health_results
    
    async def sign_document(
        self, 
        document_content: bytes, 
        certificate_id: str,
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SignatureResult:
        """
        Firmar documento con failover automático
        """
        signature_attempt = 1
        max_attempts = 2
        
        while signature_attempt <= max_attempts:
            try:
                # Seleccionar HSM provider
                hsm_provider = self.primary_hsm if signature_attempt == 1 else self.fallback_hsm
                
                if not hsm_provider:
                    raise HSMException("No HSM provider available")
                
                logger.info(f"Attempting signature with {hsm_provider.__class__.__name__} (attempt {signature_attempt})")
                
                # Validar documento antes de firmar
                self._validate_document_for_signature(document_content)
                
                # Realizar firma
                signature_result = await hsm_provider.sign_document(
                    document_content=document_content,
                    certificate_id=certificate_id,
                    user_id=user_id,
                    metadata=metadata
                )
                
                # Validar resultado
                if self._validate_signature_result(signature_result):
                    # Log exitoso
                    logger.info(f"Document signed successfully with {hsm_provider.__class__.__name__}")
                    
                    # Agregar información del proveedor usado
                    signature_result.metadata = signature_result.metadata or {}
                    signature_result.metadata.update({
                        "hsm_provider": hsm_provider.__class__.__name__,
                        "signature_attempt": signature_attempt,
                        "morocco_compliant": True
                    })
                    
                    return signature_result
                    
            except HSMException as e:
                logger.warning(f"HSM signature attempt {signature_attempt} failed: {e}")
                if signature_attempt == max_attempts:
                    raise HSMException(f"All HSM providers failed: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error during signature attempt {signature_attempt}: {e}")
                if signature_attempt == max_attempts:
                    raise HSMException(f"Signature failed after {max_attempts} attempts: {e}")
            
            signature_attempt += 1
        
        raise HSMException("Document signature failed after all attempts")
    
    async def verify_signature(
        self, 
        document_content: bytes, 
        signature: bytes,
        certificate: Optional[bytes] = None
    ) -> bool:
        """
        Verificar firma digital con múltiples proveedores
        """
        verification_results = []
        
        for name, provider in self.hsm_providers.items():
            try:
                result = await provider.verify_signature(
                    document_content=document_content,
                    signature=signature,
                    certificate=certificate
                )
                verification_results.append((name, result))
                
                # Si al menos un proveedor verifica exitosamente
                if result:
                    logger.info(f"Signature verified successfully by {name}")
                    return True
                    
            except Exception as e:
                logger.warning(f"Signature verification failed with {name}: {e}")
                verification_results.append((name, False))
        
        # Log de todos los resultados
        logger.warning(f"Signature verification results: {verification_results}")
        return False
    
    async def get_certificate_info(self, certificate_id: str) -> CertificateInfo:
        """
        Obtener información de certificado con failover
        """
        for name, provider in [("primary", self.primary_hsm), ("fallback", self.fallback_hsm)]:
            if provider is None:
                continue
                
            try:
                cert_info = await provider.get_certificate_info(certificate_id)
                logger.info(f"Certificate info retrieved from {name} HSM")
                return cert_info
                
            except Exception as e:
                logger.warning(f"Failed to get certificate info from {name} HSM: {e}")
        
        raise HSMException("Failed to retrieve certificate information from all providers")
    
    async def list_certificates(self, user_id: Optional[int] = None) -> List[CertificateInfo]:
        """
        Listar certificados disponibles
        """
        try:
            if self.primary_hsm:
                return await self.primary_hsm.list_certificates(user_id)
            elif self.fallback_hsm:
                return await self.fallback_hsm.list_certificates(user_id)
            else:
                raise HSMException("No HSM provider available")
                
        except Exception as e:
            logger.error(f"Failed to list certificates: {e}")
            return []
    
    async def generate_certificate(
        self, 
        subject_info: Dict[str, str],
        key_size: int = 2048,
        validity_days: int = 365,
        user_id: Optional[int] = None
    ) -> CertificateInfo:
        """
        Generar nuevo certificado (solo con HSM que lo soporte)
        """
        if not self.primary_hsm:
            raise HSMException("No primary HSM provider available")
        
        # Validar información del sujeto para Marruecos
        self._validate_morocco_certificate_subject(subject_info)
        
        try:
            cert_info = await self.primary_hsm.generate_certificate(
                subject_info=subject_info,
                key_size=key_size,
                validity_days=validity_days,
                user_id=user_id
            )
            
            logger.info(f"Certificate generated for subject: {subject_info.get('common_name', 'Unknown')}")
            return cert_info
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            raise HSMException(f"Failed to generate certificate: {e}")
    
    async def revoke_certificate(
        self, 
        certificate_id: str,
        reason: str = "unspecified",
        user_id: Optional[int] = None
    ) -> bool:
        """
        Revocar certificado
        """
        try:
            if self.primary_hsm:
                result = await self.primary_hsm.revoke_certificate(
                    certificate_id=certificate_id,
                    reason=reason,
                    user_id=user_id
                )
                
                if result:
                    logger.info(f"Certificate revoked: {certificate_id}, reason: {reason}")
                
                return result
            else:
                raise HSMException("No HSM provider available for certificate revocation")
                
        except Exception as e:
            logger.error(f"Certificate revocation failed: {e}")
            return False
    
    def _validate_document_for_signature(self, document_content: bytes):
        """Validar documento antes de firma"""
        if not document_content:
            raise HSMException("Document content is empty")
        
        if len(document_content) > 50 * 1024 * 1024:  # 50MB limit
            raise HSMException("Document too large for signature")
        
        # Verificar que no sea un documento ya firmado múltiples veces
        # (para evitar firmas anidadas excesivas)
        if document_content.count(b'pkcs7') > 5:
            logger.warning("Document appears to have multiple signatures")
    
    def _validate_signature_result(self, result: SignatureResult) -> bool:
        """Validar resultado de firma"""
        if not result or not result.signature:
            return False
        
        if not result.certificate:
            logger.warning("Signature result missing certificate")
            return False
        
        if not result.timestamp:
            logger.warning("Signature result missing timestamp")
        
        return True
    
    def _validate_morocco_certificate_subject(self, subject_info: Dict[str, str]):
        """Validar información del sujeto para certificados marroquíes"""
        required_fields = ["common_name", "country"]
        
        for field in required_fields:
            if field not in subject_info:
                raise HSMException(f"Missing required certificate field: {field}")
        
        # Validar país para Marruecos
        if subject_info.get("country") != "MA":
            logger.warning(f"Certificate country is not MA: {subject_info.get('country')}")
        
        # Validar formato de nombre común
        common_name = subject_info.get("common_name", "")
        if len(common_name) < 2:
            raise HSMException("Common name too short")
    
    async def get_signature_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtener estadísticas de firmas para reporting gubernamental
        """
        try:
            stats = {
                "period_days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "providers": {},
                "total_signatures": 0,
                "successful_signatures": 0,
                "failed_signatures": 0,
                "average_signature_time": 0
            }
            
            # Obtener estadísticas de cada proveedor si está disponible
            for name, provider in self.hsm_providers.items():
                if hasattr(provider, 'get_statistics'):
                    try:
                        provider_stats = await provider.get_statistics(days)
                        stats["providers"][name] = provider_stats
                        stats["total_signatures"] += provider_stats.get("total_signatures", 0)
                        stats["successful_signatures"] += provider_stats.get("successful_signatures", 0)
                        stats["failed_signatures"] += provider_stats.get("failed_signatures", 0)
                    except Exception as e:
                        logger.warning(f"Could not get statistics from {name}: {e}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting signature statistics: {e}")
            return {"error": str(e)}
    
    async def emergency_shutdown(self):
        """
        Apagado de emergencia de todos los proveedores HSM
        """
        logger.critical("EMERGENCY SHUTDOWN initiated for all HSM providers")
        
        for name, provider in self.hsm_providers.items():
            try:
                if hasattr(provider, 'shutdown'):
                    await provider.shutdown()
                    logger.info(f"HSM provider {name} shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down HSM provider {name}: {e}")
        
        self.is_initialized = False
        logger.critical("All HSM providers shut down")

# Singleton instance
_hsm_manager_instance = None

def get_hsm_manager() -> ProductionHSMManager:
    """Get singleton HSM manager instance"""
    global _hsm_manager_instance
    if _hsm_manager_instance is None:
        _hsm_manager_instance = ProductionHSMManager()
    return _hsm_manager_instance

# Funciones de conveniencia para uso en endpoints
async def sign_document_with_hsm(
    document_content: bytes,
    certificate_id: str,
    user_id: int,
    metadata: Optional[Dict[str, Any]] = None
) -> SignatureResult:
    """Función de conveniencia para firmar documentos"""
    hsm_manager = get_hsm_manager()
    return await hsm_manager.sign_document(
        document_content=document_content,
        certificate_id=certificate_id,
        user_id=user_id,
        metadata=metadata
    )

async def verify_document_signature(
    document_content: bytes,
    signature: bytes,
    certificate: Optional[bytes] = None
) -> bool:
    """Función de conveniencia para verificar firmas"""
    hsm_manager = get_hsm_manager()
    return await hsm_manager.verify_signature(
        document_content=document_content,
        signature=signature,
        certificate=certificate
    )

async def get_user_certificates(user_id: int) -> List[CertificateInfo]:
    """Función de conveniencia para obtener certificados de usuario"""
    hsm_manager = get_hsm_manager()
    return await hsm_manager.list_certificates(user_id=user_id)

async def check_hsm_health() -> Dict[str, Any]:
    """Función de conveniencia para check de salud HSM"""
    hsm_manager = get_hsm_manager()
    return await hsm_manager.health_check()