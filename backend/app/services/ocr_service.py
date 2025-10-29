# backend/app/services/ocr_service.py - Servicio OCR Síncrono

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz

logger = logging.getLogger(__name__)

class SyncOCRService:
    """Servicio OCR síncrono para procesamiento inmediato de documentos"""
    
    def __init__(self):
        self.languages = {
            'ar': 'ara',
            'fr': 'fra',
            'es': 'spa',
            'en': 'eng'
        }
        
        self.tesseract_config = {
            'ara': '--oem 3 --psm 6',
            'fra': '--oem 3 --psm 6',
            'spa': '--oem 3 --psm 6',
            'eng': '--oem 3 --psm 6'
        }
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Procesar documento con OCR de forma síncrona"""
        try:
            logger.info(f"Starting sync OCR processing for: {file_path}")
            start_time = datetime.utcnow()
            
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                result = self._process_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                result = self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'extracted_text': result['text'],
                'ocr_confidence': result['confidence'],
                'detected_language': result['detected_language'],
                'processing_time': processing_time,
                'pages_processed': result.get('pages', 1)
            }
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Procesar PDF - intentar texto directo primero, luego OCR"""
        try:
            direct_text = self._extract_pdf_text_direct(file_path)
            
            if direct_text and len(direct_text.strip()) > 50:
                logger.info("PDF has extractable text")
                return {
                    'text': direct_text,
                    'confidence': 99,
                    'detected_language': self._detect_language(direct_text),
                    'pages': self._count_pdf_pages(file_path)
                }
            else:
                logger.info("PDF requires OCR")
                return self._process_pdf_with_ocr(file_path)
                
        except Exception as e:
            logger.warning(f"PDF text extraction failed, using OCR: {e}")
            return self._process_pdf_with_ocr(file_path)
    
    def _extract_pdf_text_direct(self, file_path: str) -> str:
        """Extraer texto directo de PDF usando PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            logger.warning(f"Failed to extract text from PDF: {e}")
            return ""
    
    def _count_pdf_pages(self, file_path: str) -> int:
        """Contar páginas del PDF"""
        try:
            doc = fitz.open(file_path)
            count = doc.page_count
            doc.close()
            return count
        except:
            return 1
    
    def _process_pdf_with_ocr(self, file_path: str) -> Dict[str, Any]:
        """Procesar PDF con OCR (convertir a imágenes primero)"""
        try:
            images = convert_from_path(file_path, dpi=300)
            logger.info(f"PDF converted to {len(images)} images")
            
            all_text = ""
            total_confidence = 0
            
            for i, image in enumerate(images):
                page_result = self._process_single_image(image)
                all_text += f"\n--- Page {i + 1} ---\n{page_result['text']}\n"
                total_confidence += page_result['confidence']
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            return {
                'text': all_text.strip(),
                'confidence': round(avg_confidence),
                'detected_language': self._detect_language(all_text),
                'pages': len(images)
            }
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            raise
    
    def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Procesar archivo de imagen"""
        image = Image.open(file_path)
        result = self._process_single_image(image)
        result['pages'] = 1
        return result
    
    def _process_single_image(self, image: Image.Image) -> Dict[str, Any]:
        """Procesar una sola imagen con OCR multi-idioma"""
        try:
            best_result = {'text': '', 'confidence': 0, 'detected_language': 'es'}
            
            for lang_code, tesseract_lang in self.languages.items():
                try:
                    config = self.tesseract_config.get(tesseract_lang, '--oem 3 --psm 6')
                    
                    data = pytesseract.image_to_data(
                        image,
                        lang=tesseract_lang,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    text_parts = []
                    confidences = []
                    
                    for i in range(len(data['text'])):
                        if int(data['conf'][i]) > 0:
                            text_parts.append(data['text'][i])
                            confidences.append(int(data['conf'][i]))
                    
                    text = ' '.join(text_parts)
                    avg_conf = sum(confidences) / len(confidences) if confidences else 0
                    
                    if avg_conf > best_result['confidence'] and len(text.strip()) > 10:
                        best_result = {
                            'text': text,
                            'confidence': round(avg_conf),
                            'detected_language': lang_code
                        }
                        
                except Exception as e:
                    logger.warning(f"OCR failed for language {tesseract_lang}: {e}")
                    continue
            
            return best_result
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise
    
    def _detect_language(self, text: str) -> str:
        """Detectar idioma del texto"""
        try:
            from langdetect import detect
            detected = detect(text)
            if detected in ['ar', 'fr', 'es', 'en']:
                return detected
            return 'es'
        except:
            return 'es'
