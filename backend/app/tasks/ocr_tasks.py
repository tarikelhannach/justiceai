from celery import shared_task, chord
from datetime import datetime
import logging
import os
import sys

sys.path.insert(0, '/home/runner/workspace/backend')

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, name='app.tasks.ocr_tasks.process_document_ocr')
def process_document_ocr(self, document_id: int):
    """
    Process OCR for uploaded document.
    Runs on CPU-intensive queue for text extraction.
    Uses shared SessionLocal from app.database for proper connection pooling.
    """
    try:
        from app.database import SessionLocal
        from app.models import Document as DocumentModel
        
        logger.info(f"Starting OCR processing for document {document_id}")
        
        with SessionLocal() as db:
            document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
            
            if not document:
                logger.error(f"Document {document_id} not found in database")
                raise ValueError(f"Document {document_id} not found")
            
            file_path = document.file_path
            case_id = document.case_id
            
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "ocr_module", 
                "/home/runner/workspace/backend/app/backend-app-ocr-processor.py"
            )
            ocr_module = importlib.util.module_from_spec(spec)
            
            import app.config
            sys.modules['ocr_module.config'] = app.config
            spec.loader.exec_module(ocr_module)
            
            ocr_processor = ocr_module.MoroccoOCRProcessor()
            result = ocr_processor.process_document(file_path)
            
            document.ocr_processed = True
            document.ocr_text = result.get('extracted_text', '')
            document.is_searchable = True
            
            if 'ocr_confidence' in result:
                document.ocr_confidence = result['ocr_confidence']
            if 'detected_language' in result:
                document.ocr_language = result['detected_language']
            
            db.commit()
            
            logger.info(f"OCR processing completed for document {document_id}")
            
            return {
                'document_id': document_id,
                'text': result.get('extracted_text', ''),
                'language': result.get('detected_language', 'unknown'),
                'confidence': result.get('ocr_confidence', 0),
                'case_id': case_id
            }
        
    except Exception as exc:
        logger.error(f"OCR processing failed for document {document_id}: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        else:
            logger.critical(f"OCR processing permanently failed for document {document_id}")
            raise

@shared_task(name='app.tasks.ocr_tasks.index_document_elasticsearch')
def index_document_elasticsearch(ocr_results):
    """
    Index document in Elasticsearch AFTER OCR completes.
    Runs on IO-bound queue for network operations.
    Uses shared SessionLocal from app.database for proper connection pooling.
    
    Args:
        ocr_results: Either a list of OCR results from chord, or a single dict from chain
    """
    if isinstance(ocr_results, list):
        if not ocr_results:
            logger.error("Received empty results list")
            return {'success': False, 'error': 'No OCR results'}
        ocr_result = ocr_results[0]
    else:
        ocr_result = ocr_results
    
    document_id = ocr_result.get('document_id')
    
    try:
        from elasticsearch import Elasticsearch
        
        es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        es = Elasticsearch([es_url])
        
        if not es.ping():
            logger.error("Elasticsearch is not available")
            raise ConnectionError("Elasticsearch connection failed")
        
        index_body = {
            'document_id': document_id,
            'text': ocr_result.get('text', ''),
            'language': ocr_result.get('language', 'unknown'),
            'confidence': ocr_result.get('confidence', 0),
            'case_id': ocr_result.get('case_id'),
            'indexed_at': datetime.utcnow().isoformat(),
            'status': 'indexed'
        }
        
        es.index(
            index='judicial_documents',
            id=document_id,
            document=index_body
        )
        
        logger.info(f"Document {document_id} successfully indexed in Elasticsearch")
        
        from app.database import SessionLocal
        from app.models import Document as DocumentModel
        
        with SessionLocal() as db:
            document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found after indexing")
                raise ValueError(f"Document {document_id} disappeared during indexing")
            
            document.is_searchable = True
            db.commit()
        
        return {'success': True, 'document_id': document_id}
        
    except Exception as e:
        logger.error(f"Elasticsearch indexing failed for document {document_id}: {str(e)}")
        raise
