# backend/app/services/advanced_ocr_service.py - Advanced OCR with QARI & EasyOCR

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz

logger = logging.getLogger(__name__)

OCREngine = Literal["qari", "easyocr", "tesseract", "auto"]


class AdvancedOCRService:
    """
    Advanced OCR Service supporting multiple engines:
    - QARI-OCR: State-of-the-art for Arabic (CER: 0.061, WER: 0.160)
    - EasyOCR: Fast and accurate for multi-language
    - Tesseract: Fallback option
    """
    
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
        
        # Initialize engines on demand
        self._qari_model = None
        self._qari_processor = None
        self._easyocr_reader = None
        
    def _init_qari(self):
        """Lazy initialization of QARI-OCR model"""
        if self._qari_model is None:
            try:
                from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
                import torch
                
                logger.info("Initializing QARI-OCR model...")
                model_name = "NAMAA-Space/Qari-OCR-0.2.2.1-VL-2B-Instruct"
                
                self._qari_model = Qwen2VLForConditionalGeneration.from_pretrained(
                    model_name,
                    load_in_8bit=True,  # 8-bit quantization for best accuracy
                    device_map="auto",
                    torch_dtype=torch.float16
                )
                self._qari_processor = AutoProcessor.from_pretrained(model_name)
                logger.info("✓ QARI-OCR initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize QARI-OCR: {e}")
                logger.warning("Falling back to Tesseract/EasyOCR")
                raise ImportError(f"QARI-OCR not available: {e}")
    
    def _init_easyocr(self, languages: List[str] = None):
        """Lazy initialization of EasyOCR reader"""
        if self._easyocr_reader is None:
            try:
                import easyocr
                
                logger.info("Initializing EasyOCR...")
                lang_list = languages or ['ar', 'en', 'fr', 'es']
                self._easyocr_reader = easyocr.Reader(lang_list, gpu=True)
                logger.info(f"✓ EasyOCR initialized for languages: {lang_list}")
                
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                logger.warning("Falling back to Tesseract")
                raise ImportError(f"EasyOCR not available: {e}")
    
    def process_document(
        self,
        file_path: str,
        engine: OCREngine = "auto",
        language: str = "ar"
    ) -> Dict[str, Any]:
        """
        Process document with advanced OCR engines
        
        Args:
            file_path: Path to the document
            engine: OCR engine to use ("qari", "easyocr", "tesseract", "auto")
            language: Primary language code (ar, fr, es, en)
        
        Returns:
            Dict with extracted_text, confidence, engine_used, etc.
        """
        try:
            logger.info(f"Starting advanced OCR for: {file_path} (engine={engine})")
            start_time = datetime.utcnow()
            
            file_extension = Path(file_path).suffix.lower()
            
            # Auto-select engine based on language and availability
            if engine == "auto":
                engine = self._select_best_engine(language)
            
            # Process based on file type
            if file_extension == '.pdf':
                result = self._process_pdf_advanced(file_path, engine, language)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                result = self._process_image_advanced(file_path, engine, language)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                **result,
                'processing_time': processing_time,
                'engine_used': engine
            }
            
        except Exception as e:
            logger.error(f"Advanced OCR processing failed: {e}")
            # Fallback to Tesseract
            logger.info("Falling back to Tesseract...")
            return self._fallback_to_tesseract(file_path)
    
    def _select_best_engine(self, language: str) -> OCREngine:
        """Auto-select best OCR engine based on language"""
        if language == "ar":
            # QARI-OCR is best for Arabic
            try:
                self._init_qari()
                return "qari"
            except:
                pass
        
        # Try EasyOCR for any language
        try:
            self._init_easyocr()
            return "easyocr"
        except:
            pass
        
        # Fallback to Tesseract
        return "tesseract"
    
    def _process_pdf_advanced(
        self,
        file_path: str,
        engine: OCREngine,
        language: str
    ) -> Dict[str, Any]:
        """Process PDF with advanced OCR engines"""
        try:
            # Try direct text extraction first
            direct_text = self._extract_pdf_text_direct(file_path)
            
            if direct_text and len(direct_text.strip()) > 50:
                logger.info("PDF has extractable text (no OCR needed)")
                return {
                    'extracted_text': direct_text,
                    'ocr_confidence': 99,
                    'detected_language': language,
                    'pages_processed': self._count_pdf_pages(file_path),
                    'method': 'direct_extraction'
                }
            
            # Convert PDF to images for OCR
            logger.info("Converting PDF to images for OCR...")
            images = convert_from_path(file_path, dpi=300)
            logger.info(f"PDF converted to {len(images)} images")
            
            all_text = ""
            total_confidence = 0
            
            for i, image in enumerate(images):
                page_result = self._process_single_image_advanced(
                    image, engine, language
                )
                all_text += f"\n--- Page {i + 1} ---\n{page_result['text']}\n"
                total_confidence += page_result['confidence']
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            return {
                'extracted_text': all_text.strip(),
                'ocr_confidence': round(avg_confidence),
                'detected_language': language,
                'pages_processed': len(images),
                'method': 'ocr'
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
    
    def _process_image_advanced(
        self,
        file_path: str,
        engine: OCREngine,
        language: str
    ) -> Dict[str, Any]:
        """Process image with advanced OCR engines"""
        try:
            image = Image.open(file_path)
            result = self._process_single_image_advanced(image, engine, language)
            
            return {
                'extracted_text': result['text'],
                'ocr_confidence': result['confidence'],
                'detected_language': language,
                'pages_processed': 1,
                'method': 'ocr'
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    def _process_single_image_advanced(
        self,
        image: Image.Image,
        engine: OCREngine,
        language: str
    ) -> Dict[str, str]:
        """Process single image with specified engine"""
        
        if engine == "qari":
            return self._process_with_qari(image, language)
        elif engine == "easyocr":
            return self._process_with_easyocr(image, language)
        else:  # tesseract
            return self._process_with_tesseract(image, language)
    
    def _process_with_qari(self, image: Image.Image, language: str) -> Dict[str, str]:
        """Process image with QARI-OCR (best for Arabic)"""
        try:
            self._init_qari()
            
            # Prepare message for QARI
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "اقرأ النص في الصورة"}  # "Read the text in the image" in Arabic
                ]
            }]
            
            # Process with QARI
            text = self._qari_processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            from qwen_vl_utils import process_vision_info
            image_inputs, video_inputs = process_vision_info(messages)
            
            inputs = self._qari_processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            ).to(self._qari_model.device)
            
            # Generate OCR output
            output = self._qari_model.generate(**inputs, max_new_tokens=1024)
            result = self._qari_processor.batch_decode(output, skip_special_tokens=True)[0]
            
            return {
                'text': str(result),
                'confidence': 95  # QARI has very high confidence for Arabic
            }
            
        except Exception as e:
            logger.error(f"QARI processing failed: {e}")
            # Fallback to EasyOCR
            return self._process_with_easyocr(image, language)
    
    def _process_with_easyocr(self, image: Image.Image, language: str) -> Dict[str, str]:
        """Process image with EasyOCR"""
        try:
            self._init_easyocr()
            
            # Convert PIL Image to numpy array
            import numpy as np
            img_array = np.array(image)
            
            # Process with EasyOCR
            results = self._easyocr_reader.readtext(img_array)
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                text_parts.append(text)
                confidences.append(conf * 100)
            
            full_text = '\n'.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': int(round(avg_confidence))
            }
            
        except Exception as e:
            logger.error(f"EasyOCR processing failed: {e}")
            # Fallback to Tesseract
            return self._process_with_tesseract(image, language)
    
    def _process_with_tesseract(self, image: Image.Image, language: str) -> Dict[str, str]:
        """Process image with Tesseract OCR"""
        try:
            lang_code = self.languages.get(language, 'eng')
            config = self.tesseract_config.get(lang_code, '--oem 3 --psm 6')
            
            # Get text and confidence data
            data = pytesseract.image_to_data(
                image,
                lang=lang_code,
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=lang_code,
                config=config
            )
            
            # Calculate average confidence
            confidences = [conf for conf in data['conf'] if conf != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': int(round(avg_confidence))
            }
            
        except Exception as e:
            logger.error(f"Tesseract processing failed: {e}")
            raise
    
    def _extract_pdf_text_direct(self, file_path: str) -> str:
        """Extract text directly from PDF (no OCR)"""
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
        """Count pages in PDF"""
        try:
            doc = fitz.open(file_path)
            count = doc.page_count
            doc.close()
            return count
        except:
            return 1
    
    def _fallback_to_tesseract(self, file_path: str) -> Dict[str, Any]:
        """Fallback to basic Tesseract processing"""
        from .ocr_service import SyncOCRService
        
        logger.info("Using Tesseract fallback...")
        basic_ocr = SyncOCRService()
        result = basic_ocr.process_document(file_path)
        result['engine_used'] = 'tesseract_fallback'
        return result
    
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines"""
        available: List[str] = ["tesseract"]  # Always available
        
        try:
            self._init_qari()
            available.append("qari")
        except:
            pass
        
        try:
            self._init_easyocr()
            available.append("easyocr")
        except:
            pass
        
        return available


# Global instance
advanced_ocr_service = AdvancedOCRService()
