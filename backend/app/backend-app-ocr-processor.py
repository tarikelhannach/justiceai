# backend/app/ocr/processor.py - Procesador OCR Multi-idioma para Marruecos

import io
import os
import logging
import tempfile
import asyncio
from typing import Optional, Tuple, Dict, List, Any
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes, convert_from_path
import fitz  # PyMuPDF
from langdetect import detect, DetectorFactory
import re
import json
from datetime import datetime

from ..config import settings
from ..models import Document, DocumentType
from ..exceptions import ProcessingException

# Configurar langdetect para resultados consistentes
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class MoroccoOCRProcessor:
    """
    Procesador OCR optimizado para documentos judiciales marroquíes
    Soporta árabe, francés y español con alta precisión
    """
    
    def __init__(self):
        self.languages = {
            'ar': 'ara',  # Arabic
            'fr': 'fra',  # French  
            'es': 'spa',  # Spanish
            'en': 'eng'   # English (fallback)
        }
        
        # Configuración específica para Tesseract
        self.tesseract_config = {
            'ara': '--oem 3 --psm 6 -c tessedit_char_whitelist=أبتثجحخدذرزسشصضطظعغفقكلمنهويىءآإؤئة٠١٢٣٤٥٦٧٨٩.,;:!?()[]{}\"\'- ',
            'fra': '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÂÄÇÉÈÊËÏÎÔÖÙÛÜŸàâäçéèêëïîôöùûüÿ0123456789.,;:!?()[]{}\"\'- ',
            'spa': '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚÜÑáéíóúüñ¿¡0123456789.,;:!?()[]{}\"\'- ',
            'eng': '--oem 3 --psm 6'
        }
        
        # Patrones para detectar tipos de documentos judiciales
        self.document_patterns = {
            DocumentType.JUDGMENT: [
                r'حكم|قرار|judgment|jugement|sentencia|arrêt',
                r'المحكمة|tribunal|court|juzgado',
                r'قاضي|judge|juge|juez'
            ],
            DocumentType.ORDER: [
                r'أمر|ordre|order|orden|mandamiento',
                r'يأمر|ordonne|orders|ordena'
            ],
            DocumentType.COMPLAINT: [
                r'شكوى|دعوى|plainte|complaint|demanda|querella',
                r'المدعي|demandeur|plaintiff|demandante'
            ],
            DocumentType.MOTION: [
                r'مذكرة|mémoire|motion|escrito|alegato',
                r'الدفاع|défense|defense|defensa'
            ],
            DocumentType.CERTIFICATE: [
                r'شهادة|certificat|certificate|certificado|attestation',
                r'يشهد|certifie|certifies|certifica'
            ]
        }
        
        # Configurar Tesseract path si está especificado
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    
    async def process_document(
        self, 
        file_path: str, 
        document_id: int,
        auto_detect_language: bool = True,
        preferred_languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Procesar documento completo con OCR multi-idioma
        """
        try:
            logger.info(f"Starting OCR processing for document {document_id}")
            start_time = datetime.utcnow()
            
            # Determinar tipo de archivo
            file_extension = Path(file_path).suffix.lower()
            
            # Procesar según tipo de archivo
            if file_extension == '.pdf':
                result = await self._process_pdf(file_path, auto_detect_language, preferred_languages)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                result = await self._process_image(file_path, auto_detect_language, preferred_languages)
            else:
                raise ProcessingException(f"Unsupported file type: {file_extension}")
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Detectar tipo de documento
            document_type = self._detect_document_type(result['text'])
            
            # Preparar resultado final
            final_result = {
                'document_id': document_id,
                'text': result['text'],
                'confidence': result['confidence'],
                'detected_language': result['detected_language'],
                'languages_used': result['languages_used'],
                'document_type': document_type,
                'processing_time': processing_time,
                'pages_processed': result.get('pages_processed', 1),
                'word_count': len(result['text'].split()),
                'character_count': len(result['text']),
                'metadata': {
                    'file_type': file_extension,
                    'auto_detect_language': auto_detect_language,
                    'preferred_languages': preferred_languages,
                    'tesseract_version': pytesseract.get_tesseract_version(),
                    'processing_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"OCR processing completed for document {document_id} in {processing_time:.2f}s")
            return final_result
            
        except Exception as e:
            logger.error(f"OCR processing failed for document {document_id}: {e}")
            raise ProcessingException(f"OCR processing failed: {str(e)}")
    
    async def _process_pdf(
        self, 
        file_path: str,
        auto_detect_language: bool,
        preferred_languages: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Procesar archivo PDF"""
        try:
            # Intentar extraer texto directo primero (PDF con texto)
            direct_text = self._extract_pdf_text_direct(file_path)
            
            if direct_text and len(direct_text.strip()) > 50:
                # PDF tiene texto extraíble
                logger.info("PDF has extractable text, using direct extraction")
                detected_lang = self._detect_language(direct_text) if auto_detect_language else 'ar'
                
                return {
                    'text': direct_text,
                    'confidence': 99,  # Alta confianza para texto directo
                    'detected_language': detected_lang,
                    'languages_used': [detected_lang],
                    'pages_processed': self._count_pdf_pages(file_path)
                }
            
            else:
                # PDF escaneado, requiere OCR
                logger.info("PDF appears to be scanned, using OCR")
                return await self._process_pdf_with_ocr(file_path, auto_detect_language, preferred_languages)
        
        except Exception as e:
            logger.error(f"PDF processing error: {e}")
            # Fallback a OCR si falla extracción directa
            return await self._process_pdf_with_ocr(file_path, auto_detect_language, preferred_languages)
    
    def _extract_pdf_text_direct(self, file_path: str) -> str:
        """Extraer texto directo de PDF"""
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text_content += page_text + "\n"
            
            doc.close()
            return text_content.strip()
            
        except Exception as e:
            logger.warning(f"Failed to extract direct text from PDF: {e}")
            return ""
    
    def _count_pdf_pages(self, file_path: str) -> int:
        """Contar páginas en PDF"""
        try:
            doc = fitz.open(file_path)
            page_count = doc.page_count
            doc.close()
            return page_count
        except:
            return 1
    
    async def _process_pdf_with_ocr(
        self, 
        file_path: str,
        auto_detect_language: bool,
        preferred_languages: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Procesar PDF con OCR página por página"""
        try:
            # Convertir PDF a imágenes
            images = convert_from_path(file_path, dpi=300, fmt='png')
            logger.info(f"PDF converted to {len(images)} images for OCR")
            
            all_text = ""
            total_confidence = 0
            languages_used = set()
            
            for page_num, image in enumerate(images):
                logger.info(f"Processing PDF page {page_num + 1}")
                
                # Procesar imagen de la página
                page_result = await self._process_single_image(
                    image, 
                    auto_detect_language, 
                    preferred_languages
                )
                
                all_text += f"\n--- Página {page_num + 1} ---\n"
                all_text += page_result['text'] + "\n"
                total_confidence += page_result['confidence']
                languages_used.add(page_result['detected_language'])
            
            # Calcular confianza promedio
            avg_confidence = total_confidence / len(images) if images else 0
            
            # Detectar idioma principal del documento completo
            main_language = self._detect_language(all_text) if auto_detect_language else 'ar'
            
            return {
                'text': all_text.strip(),
                'confidence': round(avg_confidence),
                'detected_language': main_language,
                'languages_used': list(languages_used),
                'pages_processed': len(images)
            }
            
        except Exception as e:
            logger.error(f"PDF OCR processing error: {e}")
            raise ProcessingException(f"Failed to process PDF with OCR: {str(e)}")
    
    async def _process_image(
        self, 
        file_path: str,
        auto_detect_language: bool,
        preferred_languages: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Procesar archivo de imagen"""
        try:
            image = Image.open(file_path)
            result = await self._process_single_image(image, auto_detect_language, preferred_languages)
            result['pages_processed'] = 1
            return result
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise ProcessingException(f"Failed to process image: {str(e)}")
    
    async def _process_single_image(
        self, 
        image: Image.Image,
        auto_detect_language: bool,
        preferred_languages: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Procesar una sola imagen con OCR"""
        try:
            # Preprocessing de imagen
            processed_image = self._preprocess_image(image)
            
            # Determinar idiomas a probar
            languages_to_try = self._get_languages_to_try(preferred_languages, auto_detect_language)
            
            best_result = None
            best_confidence = 0
            
            # Probar OCR con diferentes idiomas
            for lang_code in languages_to_try:
                tesseract_lang = self.languages.get(lang_code, 'eng')
                config = self.tesseract_config.get(tesseract_lang, '--oem 3 --psm 6')
                
                try:
                    # Realizar OCR
                    ocr_data = pytesseract.image_to_data(
                        processed_image,
                        lang=tesseract_lang,
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Extraer texto y confianza
                    text_parts = []
                    confidences = []
                    
                    for i in range(len(ocr_data['text'])):
                        word = ocr_data['text'][i].strip()
                        confidence = ocr_data['conf'][i]
                        
                        if word and confidence > 0:
                            text_parts.append(word)
                            confidences.append(confidence)
                    
                    text = ' '.join(text_parts)
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Validar resultado
                    if text and len(text.strip()) > 10 and avg_confidence > best_confidence:
                        best_result = {
                            'text': text,
                            'confidence': round(avg_confidence),
                            'detected_language': lang_code
                        }
                        best_confidence = avg_confidence
                        
                        logger.debug(f"OCR with {tesseract_lang}: confidence={avg_confidence:.1f}, text_length={len(text)}")
                
                except Exception as e:
                    logger.warning(f"OCR failed for language {tesseract_lang}: {e}")
                    continue
            
            if not best_result:
                raise ProcessingException("OCR failed for all languages")
            
            # Detectar idioma del texto si auto-detect está habilitado
            if auto_detect_language:
                detected_lang = self._detect_language(best_result['text'])
                if detected_lang != best_result['detected_language']:
                    logger.info(f"Language detection mismatch: OCR={best_result['detected_language']}, Detection={detected_lang}")
                    best_result['detected_language'] = detected_lang
            
            # Post-procesamiento del texto
            best_result['text'] = self._post_process_text(best_result['text'], best_result['detected_language'])
            best_result['languages_used'] = [best_result['detected_language']]
            
            return best_result
            
        except Exception as e:
            logger.error(f"Single image OCR error: {e}")
            raise ProcessingException(f"Failed to process image with OCR: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocessing de imagen para mejorar OCR"""
        try:
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar si es muy pequeña o muy grande
            width, height = image.size
            if width < 1000 or height < 1000:
                # Escalar hacia arriba para imágenes pequeñas
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            elif width > 3000 or height > 3000:
                # Escalar hacia abajo para imágenes muy grandes
                scale_factor = min(3000 / width, 3000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Mejorar contraste y nitidez
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Convertir a OpenCV para procesamiento avanzado
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Aplicar filtros para mejorar calidad del texto
            # Reducción de ruido
            cv_image = cv2.medianBlur(cv_image, 3)
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Binarización adaptativa para texto
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Convertir de vuelta a PIL
            processed_image = Image.fromarray(binary)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image
    
    def _get_languages_to_try(
        self, 
        preferred_languages: Optional[List[str]],
        auto_detect: bool
    ) -> List[str]:
        """Determinar idiomas a probar para OCR"""
        if preferred_languages:
            return preferred_languages
        
        if auto_detect:
            # Para Marruecos: árabe primero, luego francés y español
            return ['ar', 'fr', 'es', 'en']
        else:
            # Idioma por defecto
            return [settings.default_language]
    
    def _detect_language(self, text: str) -> str:
        """Detectar idioma del texto"""
        try:
            if not text or len(text.strip()) < 20:
                return 'ar'  # Default para Marruecos
            
            # Detectar usando langdetect
            detected = detect(text)
            
            # Mapear códigos de idioma
            lang_mapping = {
                'ar': 'ar',
                'fr': 'fr', 
                'es': 'es',
                'en': 'en'
            }
            
            return lang_mapping.get(detected, 'ar')
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'ar'  # Default para Marruecos
    
    def _post_process_text(self, text: str, language: str) -> str:
        """Post-procesamiento del texto OCR"""
        if not text:
            return text
        
        # Limpieza general
        text = re.sub(r'\s+', ' ', text)  # Normalizar espacios
        text = text.strip()
        
        if language == 'ar':
            # Procesamiento específico para árabe
            text = self._clean_arabic_text(text)
        elif language == 'fr':
            # Procesamiento específico para francés
            text = self._clean_french_text(text)
        elif language == 'es':
            # Procesamiento específico para español
            text = self._clean_spanish_text(text)
        
        return text
    
    def _clean_arabic_text(self, text: str) -> str:
        """Limpiar texto árabe"""
        # Normalizar caracteres árabes comunes
        text = text.replace('ي', 'ي')  # Normalizar yaa
        text = text.replace('ك', 'ك')  # Normalizar kaaf
        text = re.sub(r'[ًٌٍَُِْ]', '', text)  # Remover diacríticos si es necesario
        return text
    
    def _clean_french_text(self, text: str) -> str:
        """Limpiar texto francés"""
        # Correcciones comunes de OCR en francés
        text = re.sub(r'\bIl\b', 'Il', text)  # Capitalización
        text = re.sub(r'\bEt\b', 'et', text)   # Minúscula para conjunciones
        return text
    
    def _clean_spanish_text(self, text: str) -> str:
        """Limpiar texto español"""
        # Correcciones comunes de OCR en español
        text = re.sub(r'\bY\b', 'y', text)     # Minúscula para conjunciones
        text = re.sub(r'\bO\b', 'o', text)     # Minúscula para conjunciones
        return text
    
    def _detect_document_type(self, text: str) -> DocumentType:
        """Detectar tipo de documento basado en el contenido"""
        if not text:
            return DocumentType.OTHER
        
        text_lower = text.lower()
        
        # Contar coincidencias para cada tipo
        type_scores = {}
        
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                type_scores[doc_type] = score
        
        if type_scores:
            # Retornar el tipo con mayor puntuación
            detected_type = max(type_scores, key=type_scores.get)
            logger.info(f"Detected document type: {detected_type} (score: {type_scores[detected_type]})")
            return detected_type
        
        return DocumentType.OTHER
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extraer metadatos del archivo"""
        try:
            file_stat = os.stat(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            metadata = {
                'file_size': file_stat.st_size,
                'file_type': file_extension,
                'created_date': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                'modified_date': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            }
            
            if file_extension == '.pdf':
                try:
                    doc = fitz.open(file_path)
                    pdf_metadata = doc.metadata
                    metadata.update({
                        'pages': doc.page_count,
                        'title': pdf_metadata.get('title', ''),
                        'author': pdf_metadata.get('author', ''),
                        'creator': pdf_metadata.get('creator', ''),
                        'producer': pdf_metadata.get('producer', ''),
                        'creation_date': pdf_metadata.get('creationDate', ''),
                        'modification_date': pdf_metadata.get('modDate', '')
                    })
                    doc.close()
                except:
                    pass
            
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff']:
                try:
                    with Image.open(file_path) as img:
                        metadata.update({
                            'image_size': img.size,
                            'image_mode': img.mode,
                            'image_format': img.format
                        })
                        
                        # EXIF data si está disponible
                        if hasattr(img, '_getexif') and img._getexif():
                            metadata['exif'] = dict(img._getexif())
                except:
                    pass
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}